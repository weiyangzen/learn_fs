# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/squeue.h

## Role

Public kernel header for serialized queue processing used heavily by networking.

## Key Contents

Declares opaque `squeue_t`, queue-entry setup macros, entry flags `SQ_FILL`, `SQ_NODRAIN`, and `SQ_PROCESS`, and helper macros for entering single or chained mblks into an squeue.

Defines `SQUEUE_SWITCH` for moving a connection to another squeue while executing inside one. Defines private data slots through `sqprivate_t`.

## Interfaces

Declares `squeue_init`, `squeue_create`, bind/unbind, `squeue_enter`, private data lookup, and synchronous enter/exit helpers for connections.

## Design Notes

The API stores callback procedure and argument in `mblk_t` linkage fields, so callers must pass clean mblks with null `b_next`/`b_prev`.
