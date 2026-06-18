# File Research: sources/teaching/xv6-public/memlayout.h

Defines xv6 x86 physical/virtual memory layout constants.

Contents:
- `EXTMEM`, `PHYSTOP`, and `DEVSPACE`.
- Higher-half kernel base `KERNBASE` and link address `KERNLINK`.
- Address conversion macros `V2P`, `P2V`, and assembler-safe `V2P_WO`/`P2V_WO`.

Used throughout boot, VM, device, and allocator code.
