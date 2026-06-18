# File Research: sources/os/bsd/dragonflybsd/sys/sys/vkernel.h

## Summary
Virtual-kernel process/LWP structures and virtual page-table entry definitions.

## Main Responsibilities
- Defines kernel-only vkernel LWP saved trap/ext frames, active vmspace entry, and small vmspace-entry cache.
- Defines vkernel process state with vmspace red-black tree, token, refs, and virtual CR3.
- Defines `struct vmspace_entry` and deleted-reference flag.
- Declares vkernel inheritance, exit, LWP exit, and trap hooks.
- Defines user/kernel `vpte_t` layout constants and VPTE flag bits.

## Important Behavior
Virtual kernels manage multiple VM spaces inside one process. The VPTE layout varies by `LONG_BIT`, with a four-layer page-table warning and 64-bit `vpte_t` expectation.

## Risks
The RB tree and cache references are lifecycle-sensitive. VPTE frame masks and page-bit math must match architecture page-table expectations or virtual-kernel memory translation breaks.
