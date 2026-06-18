# sources/sync-backup/casync/src/caremote.h

## Purpose
`caremote.h` declares the opaque remote transport API used by casync to pull or push chunks, indexes, and archive streams over helper protocols.

## Important APIs, Types, and Functions
The main status enum reports poll, finished, step, request, write-index, write-archive, chunk, read-index, index-eof, read-archive, and archive-eof conditions. Argument-position constants define how helper subprocesses receive operation, base URL, archive URL, index URL, and writable store URL. Public functions cover lifecycle, feature flags, digest/compression, logging/rate limiting, fds, URL/path/fd configuration, stepping/polling, chunk request/response, index/archive streaming, goodbye/abort, pending/unwritten/chunk queries, cache forgetting, and statistics.

## Control Flow
Callers configure a `CaRemote`, then repeatedly call `ca_remote_step()` and `ca_remote_poll()`. Status codes drive whether the caller should provide index/archive data, serve requested chunks, consume received data, or wait for I/O.

## State and Persistence
The `CaRemote` implementation is opaque. Persistent side effects may include cache directories and configured index/archive path writes.

## Dependencies and Integration Points
The header includes chunk and chunk ID types. It is consumed by `casync.c`, `casync-tool.c`, and helper implementations such as `casync-http.c`.

## Risks
The API has many direction-dependent operations that return `-ENOTTY`, `-EAGAIN`, `-EPIPE`, or status enums; callers must handle these carefully. The lack of visible type state in the header makes misuse possible until runtime.

## Test Signals
Integration tests provide broad coverage. Focused tests should target all status transitions and setter combinations.
