# File Research: sources/local-fs/xfsdump/common/stream.c

## Role

This file tracks stream/thread lifecycle and exit status for xfsdump/xfsrestore.

It maps pthread IDs to stream indexes, running/zombie/free states, and recorded exit code/return/hint values.

## Data Model

A static `spm` array contains up to `STREAM_SIMMAX * 3` entries, allowing multiple threads to be associated with the same stream index, such as a content thread and a drive worker thread.

Each entry stores:

- stream state
- pthread ID
- stream index
- exit code
- exit return code
- exit hint code

## Lifecycle

- `stream_init()` clears the table.
- `stream_register()` finds a free entry and records a running thread.
- `stream_dead()` marks a matching thread zombie; caller must hold the global lock.
- `stream_free()` clears an entry.

## Queries

- `stream_find_all()` returns tids whose entries match requested states.
- `stream_getix()` returns the running stream index for a tid and is intentionally lock-free because it is called from logging paths.
- `stream_get_exit_status()` returns selected status fields under lock.
- `stream_cnt()` counts unique running stream indexes.

## Exit Status Updates

`stream_set_code()`, `stream_set_return()`, and `stream_set_hint()` are generated through a macro that only allows the owning pthread to update its own running stream entry. Foreign updates are logged and ignored.

## Locking

Most table mutation and snapshot access uses the global `lock()`/`unlock()` critical section. `stream_find()` itself does not lock and is used by callers that already hold the lock or by special logging contexts.
