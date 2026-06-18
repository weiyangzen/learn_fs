# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/SYS.h

This i386 syscall header defines `int $0x80` syscall stubs, with an optional `I686_LIBC` `sysenter` path. It provides pseudo, no-error, raw, and weak wrappers, and PIC-safe jumps to hidden `__cerror` when the carry flag indicates syscall failure.
