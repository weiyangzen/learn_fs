# File Research: sources/local-fs/xfsprogs/db/init.h

## Purpose
Declares process-wide xfs_db globals initialized by `init.c`.

## Interfaces
- Exposes `blkbb`, `exitcode`, `expert_mode`, `mp`, `x`, and `cur_agno`.

## Dependencies
Included by most command implementations to access mount geometry, exit status, mode gating, and libxfs initialization state.
