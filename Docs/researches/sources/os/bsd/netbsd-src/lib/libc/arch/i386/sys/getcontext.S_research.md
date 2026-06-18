# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/getcontext.S

This i386 `getcontext` wrapper calls the syscall, then adjusts the saved `%eip` to the caller return address, saved `%esp` to the post-return stack position, and saved `%eax` to zero.
