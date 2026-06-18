# File Research: sources/os/plan9/plan9/sys/src/9/omap/rebootcode.s

OMAP reboot trampoline copied to low memory and executed during kernel replacement.

Key responsibilities:
- `main(PADDR(entry), PADDR(code), size)` disables interrupts, slows speculative/cached behavior, turns caches off, switches from `KZERO` to physical DRAM addressing, disables MMU/caches, copies the new kernel image to its destination, flushes caches, and branches to the physical entry point.
- `cachesoff` writes back caches, disables I/D caches, re-establishes the physical/KZERO double map, invalidates TLBs, and adjusts SB/SP/LR into physical addressing.
- Provides local `_r15warp` and stubs for `panic` and `pczeroseg`.

Important behavior:
- Must fit in the low-memory space before page tables.
- Uses early `PUTC` progress characters to the serial console.
- Avoids `R11` because the loader uses it as a temporary.
- Jumps to the physical kernel entry; the new kernel later establishes virtual addressing in `l.s`.

Dependencies:
- Depends on `arm.s`, `cache.v7.s`, `memmove`, cache helpers, and the same page-table layout as `l.s`.

Notable risks:
- Runs while dismantling the current virtual-memory environment, so address-segment adjustment is central and fragile.
- Assumes the copied image and entry/destination arguments are sane physical addresses.
