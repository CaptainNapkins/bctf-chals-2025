# Solve

## Source Analysis
It looks like the first time the program prompts us for input we can input 5 characters. These 
characters then get printed back out to us. However, these characters are printed back out to us 
via `printf` without a format specififer. So, we can input our own format specifier to leak 
info off the stack. This is called a format string vulnerability. 

Next, we are prompted for two more pairs of numbers. Once we have done this the program does 
something interesting with these numbers. It takes the first set, `s1` and `d1` and does the
following; it treats `s1` like a pointer, de references it, and places the value of `d1` at that 
location. So, our value `d1` is being placed at the place pointed to by `s1`. The same thing is 
done with the second pair `s2` and `d2`. This behavior essentially gives us an arbitrary write 
primitive. We can pick two places in memory and put whatever we want there. So to recap, we've got 
ourselves an info leak in the form of a printf vulnerability and we can write to two arbitrary 
places in memory. 

It should be mentioned that this binary has full protections. In order to know where we would be 
writing we'd need to leak a binary address, libc address, or a stack address. 

## Our exploit
This exploit took me a while to put together. I decided I was going to try a GOT overwite. But, 
not a traditional one; the binary itself had full RELRO, meaning that its GOT was not writeable. But,
the libc's GOT only had partial RELRO meaning it was write-able. So it stands to reason that if we 
can leak a libc address via the format string vulnerability we could use our arbitary write to 
overwrite something in the GOT. 

After our arbitrary writes `printf` is called. Why dont we look in printf to see if there is 
anything useful we can overwrite. It turns out that `printf` calls two libc GOT functions. 
1. `__strchrnul_sse2`
2. `__memmove_ssse3`

For this exploit we'll work with the seccond one. What we've got so far:

1. Leak libc via the format string. `__libc_start_call_main` is on the stack so we'll grab that. 
2. Use the first write to overwrite the libc got address of `__memmove_ssse3`. 

What are we gonna overwrite it with? Why, `gets()` of course! At the point that we overwrite that
GOT address with `gets()` there happens to be a stack pointer in `rdi`. So, when we call `gets()`, 
we can read input into that stack pointer. Input like `/bin/sh` perhaps??

But what about our second write? Well, within `gets()` There is another libc GOT function called. Specifically, its called in `__IO_getline_info`. This is crucially called after our input is processed,
meaning when the libc GOT function is called within `gets()`, a pointer to `/bin/sh` is already in 
`rdi`. The libc GOT function in question is `__memchr_sse2`. 

So, our second write will overwrite `__memchr_sse2` with `system`. That way when it is called 
`/bin/sh` will be in `rdi` and we can pop a shell. 

Our exploit chain looks like this:

leak libc via printf -> overwrite `__memmove_ssse3` with (gets + 4) -> send in `/bin/sh` so it gets
placed into the stack pointer in `rdi` -> overwrite `__memchr_sse2` in `gets()` with system -> pop 
a shell. 

And that's what we do! I was having a hard time getting this exploit to work; I was trying a bunch 
of one gadgets, and in these libc functions where the registers are filled with junk, none of the 
conditions were satisfied. This was a cool opportunity to use a non-conventional GOT overwrite 
technique to pop a shell. I think its super cool how GOT overwrites can be chained together like this
to get code execution, and I'm sure there are more combos to achieve different effects. 

There was also a cool technique after the CTF I saw where someone used these arbitrary writes to
overwrite exit handlers. I shall be looking into that more. 

Thanks to my teammates for making this an awesome b01lersCTF. Without them none of this would be 
possible. 
