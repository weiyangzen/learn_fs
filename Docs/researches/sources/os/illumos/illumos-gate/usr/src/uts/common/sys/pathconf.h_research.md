# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pathconf.h

## Purpose
Defines the kernel/user structure used to carry POSIX `pathconf()` limits, especially for the historical static NFSv2 pathconf mount kludge.

## Main Interfaces
- Bitset helpers:
  - `_BITS`
  - `_PC_N`
  - `_PC_ISSET()`
  - `_PC_SET()`
  - `_PC_ERROR`
- `struct pathcnf`: link/name/path/pipe/terminal pathconf values plus a mask encoding boolean values or errno state.
- `struct pathcnf32`: 32-bit syscall-compatible layout under `_SYSCALL32`.
- Kernel helpers:
  - `PCSIZ`
  - `PCCMP()`

## Dependencies And Relationships
Includes `sys/unistd.h` for `_PC_*` names and system types. NFS mount code historically stores this data locally for servers that could not answer pathconf via protocol.

## Research Notes
`pc_mask` encodes both boolean pathconf features and whether individual fields should be treated as errors. Kernel-only trailing fields add reference counting and a linked-list pointer without changing `PCSIZ`, the comparable non-kernel prefix.
