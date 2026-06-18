# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/aarch64/crt0.S

AArch64 process entry stub. It aliases `_start` to `__start`, moves the kernel/loader-provided `ps_strings` value from `x2` to `x1`, and branches to common `___start`.

The cleanup function remains in `x0`, matching the common C signature `___start(cleanup, ps_strings)`.
