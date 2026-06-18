# File Research: sources/os/linux/linux/io_uring/cancel.h

## Purpose
Defines shared cancellation data and declarations for io_uring cancellation paths.

## Main Contents
- `struct io_cancel_data`: context, user data, file, opcode, flags, and cancel sequence.
- Prototypes for async cancel prep/issue, generic try-cancel, sync cancel, request matching, task-safe matching, list removal helpers, context cancellation, and generic task cancellation.
- `io_cancel_match_sequence()`: inline helper that records and detects per-request cancel sequence reuse.

## Cross-File Relationships
- Implemented mainly by `cancel.c`.
- Included by `futex.h`, `fdinfo.c`, and other cancel-aware io_uring modules.

## Risks / Review Notes
- `io_cancel_match_sequence()` mutates request cancel sequence state; it must only be used as part of the intended cancel matching flow.
