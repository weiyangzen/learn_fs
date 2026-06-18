# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/__vfork14.S

This i386 `__vfork14` wrapper saves the return address in `%ecx`, uses the old `int $0x80` trap to avoid clobbering it, normalizes parent/child return values through `%edx`, and jumps directly back through `%ecx`.
