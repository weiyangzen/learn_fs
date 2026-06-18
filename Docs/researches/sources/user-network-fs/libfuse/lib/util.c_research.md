# sources/user-network-fs/libfuse/lib/util.c

## Purpose
Small libfuse utility implementation for strict integer parsing and optional thread naming.

## Important APIs, Types, And Functions
- `libfuse_strtol` parses a base-10 `long`, rejects null, empty, trailing garbage, and propagates `errno` as negative errno.
- `fuse_set_thread_name` calls `pthread_setname_np(pthread_self(), name)` when configured.

## Control Flow
`libfuse_strtol` clears `errno`, calls `strtol`, validates the end pointer, and writes the result only on success. Thread naming is compile-time conditional and otherwise a no-op.

## State And Persistence
No persistent state. Thread names are process/thread metadata only.

## Dependencies And Integration Points
Used by mount helpers to parse fd environment variables and likely by other libfuse internals. Depends on `fuse_config.h` feature detection and `pthread` only when available.

## Risks
Parsing does not reject leading whitespace because `strtol` permits it; callers needing stricter syntax should prevalidate. There is a duplicate `#include <errno.h>`, harmless but noisy.

## Test Signals
Test null, empty, whitespace, signs, overflow, trailing text, and valid fd strings; build with and without `HAVE_PTHREAD_SETNAME_NP`.
