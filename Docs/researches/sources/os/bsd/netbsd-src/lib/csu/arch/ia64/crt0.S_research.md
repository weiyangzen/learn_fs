# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/ia64/crt0.S

IA-64 process entry stub. It documents kernel-provided inputs: cleanup, object pointer, `ps_strings`, and stack pointer.

The code sets `sp` from `in3`, moves `ps_strings` into the second argument slot, adjusts the register backing store with `alloc`, and calls `___start`.
