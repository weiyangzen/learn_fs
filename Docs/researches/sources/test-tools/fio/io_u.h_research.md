# sources/test-tools/fio/io_u.h

## Purpose
Defines `struct io_u`, its flags, and the public API for fio I/O unit allocation, preparation, accounting, completion, and buffer filling.

## Important APIs, Types, and Functions
Flags include free/in-flight/current-depth markers, file-put suppression, trim/barrier/verify/pattern/device-error/zeroed/error state, and ZBD verification flags. `struct io_u` stores timing, file pointer, direction and accounting direction, write sequence number, priority, trim count, buffer and transfer state, random seed, verify offset, residual/error fields, engine private data, verify/workqueue union, ZBD callbacks, completion callback, data placement fields, and engine-specific unions for libaio, POSIX AIO, SGIO, Solaris AIO, RDMA, and mmap. Declared functions cover get/put/requeue, completion, queue state, error logging, depth maps, buffer filling, sync, trim, and queue fullness.

## Control Flow
The header describes objects flowing from freelist to preparation to engine queue to completion and back to freelist, with optional requeue for partial transfers or verify/trim backlog reuse.

## State and Persistence Behavior
`io_u` is transient runtime state. Its fields drive persistent I/O effects on target files/devices and the stats/log records emitted by fio.

## Dependencies and Integration Points
Includes compiler, OS, direction, debug, file, workqueue, and optional engine headers. It is central to ioengine implementations and fio core scheduling.

## Risks
The struct is shared across many engines and feature macros, so layout and field semantics are compatibility-sensitive. Flag handling must be consistent between core and engines. `acct_ddir()` treats `-1` as unset in an enum field, matching initialization in `io_u.c`.

## Test Signals
Engine build coverage across optional backends, async/sync jobs, verify paths, trim paths, and debug builds with `dprint_io_u()` enabled provide coverage.
