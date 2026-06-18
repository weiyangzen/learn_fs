# File Research: sources/os/plan9/9front/sys/src/9/pc/ether8003.c

## Purpose
Western Digital/SMC WD8003/WD8013 and SMC 8216 Ethernet driver using the shared DP8390 core.

## Exposed Interface
- Link function: `ether8003link()`
- Registers:
  - `addethercard("WD8003", reset)`

## Implementation Notes
- Handles 83C584 bus interface registers, old “dumb” 8003E aliasing behavior, 16-bit card detection, and 8216 alternate register set.
- `reset()` sets defaults (`port=0x280`, `irq=3`, `mem=0xD0000`, `size=8KiB`), reserves I/O ports, reads LAN address ROM, validates checksum, allocates `Dp8390`, and dispatches to `reset8003()` or `reset8216()`.
- `reset8003()` detects cards without a full interface chip, derives memory/IRQ/width, detects 16-bit operation, enables interface RAM, and sets LAN/memory width bits.
- `reset8216()` reads memory/IRQ settings through alternate registers, enables RAM/interrupts, and forces 16-bit width.
- Sets DP8390 ring pages, calls `dp8390reset()`, copies station address if not overridden, and calls `dp8390setea()`.
- Claims upper memory block with `umballoc()` and warns if unavailable.

## Filesystem Relevance
Network driver only. Relevant to low-level PC memory/I/O resource handling and legacy NIC shared-memory buffer setup, which resembles old block-device memory window constraints.

## Risks / Quirks
- Many compatibility paths for old cards rely on register aliasing/probing.
- Default memory/IRQ assumptions target old ISA hardware.
- Failure to reserve UMB memory only logs a warning after hardware init.
