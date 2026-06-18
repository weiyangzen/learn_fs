# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/SYS.h

This header defines HPPA syscall wrapper macros around the HPPA syscall gateway. It saves/restores `%rp`, places syscall numbers in `%t1`, branches to hidden `__cerror` on failure, and provides pseudo, no-error, raw, and weak syscall macro variants.
