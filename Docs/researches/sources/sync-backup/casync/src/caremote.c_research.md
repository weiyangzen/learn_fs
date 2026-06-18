# sources/sync-backup/casync/src/caremote.c

## Purpose
`caremote.c` implements casync's remote transport engine. It manages feature negotiation, subprocess or fd-based I/O, framed protocol parsing/emission, disk-backed chunk request queues, local cache storage for received chunks, streamed index/archive files, chunk validation, and cooperative step/poll operation.

## Important APIs, Types, and Functions
`struct CaRemote` stores connection state, URL/callout configuration, cache configuration, input/output fds, input/output/chunk/validation buffers, queue cursors, feature flags, index/archive file state, last chunk, subprocess pid, digest/compression configuration, and request statistics. Public setters configure feature flags, URLs, cache, local files/fds, digest, compression, log level, and rate limit. The core engine is `ca_remote_step()` and `ca_remote_poll()`. Pull APIs include `ca_remote_request()`, `ca_remote_request_async()`, and `ca_remote_next_chunk()`. Push APIs include `ca_remote_next_request()`, `ca_remote_can_put_chunk()`, `ca_remote_put_chunk()`, and `ca_remote_put_missing()`. File streaming APIs cover index and archive read/write/eof. Termination APIs are `ca_remote_goodbye()` and `ca_remote_abort()`.

## Control Flow
`ca_remote_start()` validates local flags, starts an ssh/helper subprocess when fds were not injected, opens configured index/archive paths according to negotiated direction, and transitions after hello negotiation. `ca_remote_step()` clears transient file buffers, starts the remote, flushes output, sends hello, processes one input frame, sends queued requests, streams index, streams archive, and reads more input, returning status codes that tell callers whether to poll or react. `ca_remote_process_message()` validates frame size/type/state and dispatches to hello, index/archive, request, chunk, missing, goodbye, or abort handlers. Request sending batches IDs with matching priority into a single request frame while output is below a low watermark.

## State and Persistence
The remote cache is a directory, caller-provided or temporary, containing chunk files plus symlink queue directories `chunks/`, `low-priority/`, and `high-priority/`. Temporary caches are removed on unref; non-temporary caches have queue symlinks removed. Index/archive writes go through temporary paths and are renamed into place on completion/goodbye. Queue cursors are in memory, while symlink farms persist enough to check duplicate queued chunks. Request counters track successful chunk reads and bytes.

## Dependencies and Integration Points
The module depends on protocol definitions, chunk file helpers, compression/digest helpers, realloc buffers, rm-rf cleanup, process execution, poll, and utility code. `casync.c` and `casync-tool.c` include `caremote.h` for high-level sync operations. `casync-http.c` is one helper that speaks this protocol over stdio. The remote callout resolution uses `CASYNC_PROTOCOL_PATH`, `CASYNC_SSH_PATH`, and `CASYNC_REMOTE_PATH`.

## Risks
The state machine is sensitive to feature-flag compatibility and direction checks. Disk-backed queues use symlinks and in-memory cursors, so partial cache reuse or external mutation can produce stale or skipped entries. `ca_remote_set_archive_fd()` appears to call `ca_remote_file_set_fd(&rr->index_file, fd)` instead of `archive_file`, which would misdirect archive fd configuration. `ca_remote_abort()` calls `strlen(message)` without a NULL check. The subprocess child path has branches that call `return log_oom()` after fork instead of `_exit`, which is worth auditing. Digest autodetection is flexible but can hide mismatched expected algorithms unless callers set a digest explicitly.

## Test Signals
End-to-end script tests exercise remote helpers through `CASYNC_PROTOCOL_PATH`, especially make/extract flows and seed use. There is no focused unit test visible for frame validation, queue ordering, subprocess argument construction, or the archive fd setter. These are high-value test targets.
