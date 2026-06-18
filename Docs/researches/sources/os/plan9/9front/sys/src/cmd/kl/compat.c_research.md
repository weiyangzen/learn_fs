# File Research: sources/os/plan9/9front/sys/src/cmd/kl/compat.c

Thin compatibility inclusion unit for the SPARC linker. It includes `l.h` and then the shared compiler/linker compatibility body from `../cc/compat`.

There is no local logic here; its purpose is to compile common compatibility routines in the `kl` build with the linker’s declarations and global context available.
