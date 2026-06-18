# File Research: sources/os/plan9/plan9/sys/src/9/kw/mmu.c

## Role

Kirkwood ARM MMU management. It initializes kernel mappings, manages per-process L1/L2 page-table entries, switches address spaces, maps kernel IO windows, and supports uncached/vmapped memory.

This is virtual-memory infrastructure with direct impact on driver DMA and storage buffers.

## Main Interfaces

- Diagnostics/init:
  - `mmudump`
  - `mmuidmap`
  - `mmuinit`
- Process MMU:
  - `mmuswitch`
  - `flushmmu`
  - `mmurelease`
  - `putmmu`
- Kernel mappings:
  - `mmuuncache`
  - `mmukmap`
  - `mmukunmap`
  - `cankaddr`
  - `vmap`
  - `vunmap`

## Important Behavior

- `mmuinit` maps kernel segments, IO, boot ROM, and configured physical memory.
- Uses ARM L1 section mappings and L2 small page mappings.
- Maintains per-process L1/L2 tables through `Proc.pmmu`.
- `putmmu` allocates L2 tables as needed and installs user mappings with appropriate AP/cache bits.
- Flushes D/I caches and invalidates TLBs on mapping changes.
- `vmap` allocates kernel virtual space and maps physical pages for device access.
- `mmuuncache` clears cacheable/bufferable bits for a virtual address range.

## Dependencies And Assumptions

- Uses ARM PTE constants from `arm.h`.
- Uses `KMAP`, `KZERO`, `PTEMAPMEM`, and physical constants from `mem.h`.
- Relies on assembly helpers from `l.s`.

## Notable Risks

- TLB/cache ordering is critical and manually maintained.
- `mmuuncache` mutates page-table attributes in place and must be used carefully with live cached aliases.
- Kernel mapping functions assume ranges are page-aligned or roundable to pages.
