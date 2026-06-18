# sources/object-store/rustfs/crates/protocols/src/sftp/driver.rs

## Purpose
`driver.rs` defines `SftpDriver`, the per-session `russh_sftp::server::Handler` that translates SFTPv3 packets into S3-like `StorageBackend` operations. It centralizes authenticated session context, read-only mode, the handle table, multipart and read-cache limits, backend deadlines, and the `SessionDiag` activity stamp used by watchdogs. It also owns `Drop` cleanup for live multipart uploads, making it the safety boundary between an SSH channel lifetime and backend object state.

## Important APIs, Types, and Functions
`SftpDriver::new` wires storage, credentials, limits, read-cache accounting, and diagnostics into a fresh empty handle table. Helper APIs include `access_key`, `secret_key`, `enforce_server_readonly`, `with_handle_ref`, `allocate_handle`, `run_backend`, `run_backend_with_err`, and `authorize`. `run_backend` wraps every backend future in the configured timeout and maps backend errors through `s3_error_to_sftp`; `run_backend_with_err` preserves typed backend errors for branches that need not-found detection. `authorize` preserves policy denial as `PermissionDenied` and IAM unavailability or timeout as `Failure`.

The `Handler` implementation covers SFTPv3 packet dispatch: version negotiation, realpath, stat/lstat/fstat, opendir/readdir, open/read/write/close, remove/mkdir/rmdir/rename, setstat/fsetstat, and unsupported symlink/readlink/extended requests. Several bodies delegate to sibling modules such as `read.rs`, `write.rs`, `dir.rs`, and `attrs.rs`.

## Control Flow
Handler methods stamp `session_diag` on entry and exit. `open` rejects append, mixed read/write, and malformed `EXCL` or `TRUNC` flags before dispatching to read or write open paths. `read` delegates to `read_inner` and treats `Eof` as normal control flow. `write` removes the handle before awaiting write dispatch, inserting a tombstone first when the state already owns an upload id so cancellation leaves `Drop` enough data to abort. `close` removes the handle, commits buffered writes via `PutObject`, completes multipart streams, or aborts failed streams. `rename` HEADs the source, uses `CopyObject` up to the 5 GiB single-shot ceiling, uses multipart copy above that, and then deletes the source.

## State and Persistence Behavior
The handle table is session-local state. Read handles cache attrs and object size. Write handles hold a `WritePhase` that may reference persistent multipart upload ids. Tombstones are deliberately inserted before cancellation-sensitive awaits. `Drop` drains handles, finds active uploads with cached abort authorization, and spawns bounded fire-and-forget `AbortMultipartUpload` tasks under a global permit pool. If abort is denied, permit acquisition fails, the runtime shuts down, or abort times out, cleanup depends on bucket lifecycle rules.

## Dependencies and Integration Points
The driver depends on `StorageBackend`, IAM authorization, `SessionContext`, `MaskedAccessKey`, SFTP protocol types, `s3s` multipart/copy DTOs, UUID handles, Tokio timeouts/semaphores, and tracing. It integrates with `state.rs`, `paths.rs`, `errors.rs`, `read_cache.rs`, `lifecycle.rs`, and operation modules for reads, writes, attrs, and directory behavior.

## Risks and Test Signals
Key risks are cancellation during multipart operations, timeout-created orphan uploads, non-atomic rename, stale cached abort authorization after policy changes, read-only enforcement drift, and generic failure on handle exhaustion. Tests cover version advertisement, activity stamping, fstat behavior, realpath sanitization and traversal collapse, no-backend realpath, read-only setstat/fsetstat rejection, directory-empty error propagation, and authorization status separation.
