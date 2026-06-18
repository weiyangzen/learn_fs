# sources/object-store/rustfs/crates/protocols/src/sftp/read.rs

## Purpose
`read.rs` implements read-side SFTP behavior: opening objects for read, serving `SSH_FXP_READ`, draining backend range streams, and populating the per-handle read-ahead cache.

## Important APIs, Types, and Functions
`open_read` parses the path, requires bucket plus object, authorizes `GetObject`, HEADs metadata, builds SFTP attrs, creates a `ReadCache`, and allocates `HandleState::File`. `read_inner` performs read request validation, cache probing, backend range fetch, and response slicing. `fetch_object_range` wraps both the initial range call and each body chunk wait in timeout/error mapping. `try_populate_read_cache` applies the soft process-wide cache limit before populating the handle cache.

## Control Flow
Zero-length reads return `BadMessage` before range math. Requested length is capped by `MAX_READ_LEN`. Non-file handles fail. `offset >= size` returns `Eof` before backend access. Cache hits return immediately and may be short at a window boundary. Cache misses re-authorize, fetch a window at least as large as the requested bytes, return EOF on empty backend data, slice the client response from the front, and offer the full window to the cache.

## State and Persistence Behavior
Read handles persist size and attrs captured at open, so concurrent object replacement is not reflected. `ReadCache` is per handle, while `read_cache_in_use` is process-wide. The memory ceiling is a soft cap because concurrent sessions can populate between relaxed checks. `READ_CACHE_DISABLED` bypasses retention.

## Dependencies and Integration Points
The module depends on attrs helpers, constants, `SftpDriver`, error mapping, path parsing, `HandleState`, `StorageBackend`, IAM `S3Action::GetObject`, stream utilities, and SFTP data/handle types. It is invoked from `driver.rs` open/read methods.

## Risks and Test Signals
Risks include stale size metadata, cache-edge short reads, body-stream stalls after an initial successful range call, soft memory-limit overshoot, and repeated authorization on cache misses. Tests cover zero-length rejection, EOF before backend calls, normal reads, EOF logging silence, backend failure logging, stalled body timeout, sequential cache hits, window crossing, partial edge hits, and disabled cache behavior.
