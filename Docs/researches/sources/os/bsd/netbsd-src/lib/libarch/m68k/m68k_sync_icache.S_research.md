# File Research: sources/os/bsd/netbsd-src/lib/libarch/m68k/m68k_sync_icache.S

Assembly wrapper for m68k instruction-cache synchronization.

Key behavior:
- Defines `ENTRY(m68k_sync_icache)`.
- Loads stack arguments into `%a1` and `%d1`.
- Loads syscall/trap selector `0x80000004` into `%d0`.
- Executes `trap #12`, then returns.

Dependencies:
- `<machine/asm.h>` entry macro.
- m68k kernel trap ABI for cache synchronization.

Notes:
- The file has no local bounds checking; it is an ABI-level wrapper.
