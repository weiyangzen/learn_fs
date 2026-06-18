# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rtsummary.h

## Purpose
Defines shared state and declarations for realtime summary scrub and repair.

## Major Components
- `struct xchk_rtsummary`: contains optional temp-exchange state, rtalloc args, computed geometry, reservation blocks, xfile copyout position, and flexible suminfo buffer.
- `xfsum_copyout`: exported helper to copy staged summary words out of the xfile.
- `xrep_setup_rtsummary`: repair setup declaration or no-op stub.

## Control Flow and Invariants
The flexible `words[]` buffer is used as a block-sized comparison/copy buffer for staged summary data. Geometry fields are computed during setup and consumed by scrub and repair.

## Dependencies and Integration
Shared by `rtsummary.c` and the corresponding repair implementation. Uses realtime allocation args and online repair temporary exchange state when available.

## Risk and Edge Cases
Callers must allocate the flexible array large enough for `mp->m_blockwsize` suminfo words, as done by `xchk_setup_rtsummary`.
