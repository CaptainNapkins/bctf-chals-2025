all:
	gcc chal.c -Wl,-z,relro -O0 -o chal
patch:
	patchelf --set-interpreter ./ld-2.38.so --set-rpath . chal
