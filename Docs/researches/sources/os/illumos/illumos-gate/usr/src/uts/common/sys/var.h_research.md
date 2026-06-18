# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/var.h

## Role

Defines legacy system configuration tunable structure `struct var`.

## Key Interfaces

- `struct var` contains counts/limits for I/O buffers, callouts, processes, user processes, scheduler priorities, clists, buffer hash state, physical I/O buffers, system virtual allocation map size, maximum physical memory, delayed-write age, and buffer cache high-water mark.
- Exports global `struct var v`.

## Risk Notes

This is historical system configuration ABI/state. Many fields may be obsolete or compatibility-only, but consumers still depend on names and layout.
