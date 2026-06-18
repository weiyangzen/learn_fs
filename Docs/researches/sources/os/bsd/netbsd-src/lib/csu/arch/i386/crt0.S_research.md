# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/i386/crt0.S

i386 process entry stub. It hides `___start`, aliases `_start` to `__start`, pushes `%ebx` and `%edx`, and calls `___start`.

The pushed register order supplies the common `cleanup` and `ps_strings` arguments according to the i386 entry convention.
