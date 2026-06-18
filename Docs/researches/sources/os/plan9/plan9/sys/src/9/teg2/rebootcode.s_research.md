# File Research: sources/os/plan9/plan9/sys/src/9/teg2/rebootcode.s

Relocatable ARMv7 reboot trampoline copied to `REBOOTADDR`.

Key behavior:
- Disables caches, reinstalls temporary double mappings, invalidates TLBs, and switches from `KZERO` to physical DRAM addressing.
- Turns off the MMU.
- Copies a loaded replacement kernel from physical source to physical destination.
- Branches to the new kernel entry in physical addressing.

Important functions:
- `main(entry, code, size)`: trampoline entry.
- `cachesoff`: cache/MMU preparation before final MMU disable.
- `_r15warp`: segment-adjusts return PC and SP.
- `panic` and `pczeroseg`: local stubs required by included cache code.

Notes:
- Must fit below the page-table area, per `mem.h`.
- Includes `cache.v7.s` so the trampoline is self-contained after copying.
