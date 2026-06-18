# File Research: sources/os/bsd/netbsd-src/sys/kern/core_netbsd.c

## Purpose
Implements the historic NetBSD native core file format.

## Main Interfaces
- `CORENAME(real_coredump_netbsd)()` fills the core header, invokes CPU-specific core dumping, writes the header, writes CPU state, and walks UVM mappings to write segments.
- `CORENAME(coredump_writesegs_netbsd)()` writes a `coreseg` header and corresponding user memory for each dump segment.

## Implementation Notes
The file is macro-parameterized with `CORENAME` and optional `COREINC`, allowing format variants. Segment flags distinguish stack from data with `CORE_STACK`/`CORE_DATA`.

## Dependencies
Uses `sys/core.h`, CPU coredump hooks, UVM coredump walk/count hooks, coredump write hooks, and process VM sizing fields.
