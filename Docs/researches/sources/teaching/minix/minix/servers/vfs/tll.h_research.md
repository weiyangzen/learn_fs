# File Research: sources/teaching/minix/minix/servers/vfs/tll.h

## Purpose
Declares the three-level-lock types and structure used throughout VFS.

## Main Definitions
- `tll_access_t`: `TLL_NONE`, `TLL_READ`, `TLL_READSER`, `TLL_WRITE`.
- `tll_status_t`: default state, pending upgrade, and pending wake state.
- `tll_t`: current mode, owner, shared reader count, status flags, and two worker queues.

## Dependencies
References `struct worker_thread`, defined in `threads.h`.

## Risks and Notes
The comments describe `TLL_UPGR` as an upgrade marker; the structure comment also mentions pending state. The actual semantics are implemented in `tll.c`.
