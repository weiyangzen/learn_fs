# File Research: sources/os/plan9/plan9/sys/src/9/kw/devarch.c

## Purpose
Implements the `#P` architecture device namespace for Kirkwood, exposing architecture-specific read/write files and CPU/timebase information.

## Behavior
- Maintains a fixed-size `archdir` table plus matching read/write callback arrays.
- `addarchfile` adds immutable named files to `#P`, rejecting duplicates and paths beyond `Qmax`.
- Standard device methods attach, walk, stat, open, close, read, and write through Plan 9 device helpers.
- `archread` dispatches directory reads and per-file read callbacks.
- `archwrite` dispatches per-file write callbacks or rejects with `Eperm`.

## Exposed Files
- `cputype`: read via `cputyperead`, reporting ARM/Marvell SoC identity and CPU MHz.
- `timebase`: read via `tbread`, reporting cycle counter hex.
- `nsec` support exists as `nsread` but is commented out in `archinit`.

## Hardware Identification
- `cputype2name` reads the SoC/device ID through PCIe and CP15, identifies Marvell/ARM926EJ-S architecture, and decodes known 88F6281 revisions (`Z0`, `A0`, `A1`).

## Dependencies and Integration
Uses Plan 9 device table plumbing, `soc` register mappings, CP15 ID helper `cpidget`, PCIe register layout from `io.h`, and `cycles`.

## Risks and Notes
The file table is capped at 16 entries and cannot delete files. CPU naming relies on the same unusual PCIe-derived device identity approach noted in the code.
