<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/error_mapping.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/wrappers/error_mapping.go

Purpose: FUSE filesystem wrapper that converts internal, GCS, gRPC, HTTP, and context errors into `syscall.Errno` values understood by the kernel, while recovering panics with fatal logging.

Important APIs/types/functions: package variable `DefaultFSError`; helper `errno`; constructor `WithErrorMapping`; type `errorMapping`; methods `handlePanic`, `mapError`, and delegators for all `fuseutil.FileSystem` operations.

Control flow: each method defers panic handling, calls the wrapped filesystem method, and passes the result to `mapError`. `errno` first preserves nil, maps `gcsfuse_errors.FileClobberedError` to `ESTALE`, preserves existing `syscall.Errno`, maps context cancellation and storage object-not-exist, handles selected string patterns, maps gRPC status codes, maps `googleapi.Error` HTTP codes, and falls back to `EIO`.

State and persistence behavior: stateless wrapper, aside from references to wrapped filesystem and global default errno. It affects runtime error state seen by FUSE and outer wrappers.

Dependencies and integration points: used by `fs.NewServer` as the innermost wrapper before tracing/monitoring. Integrates with Cloud Storage errors, google API errors, gRPC status, gcsfuse clobber errors, logger, and every FUSE operation interface.

Risks: error matching by string is brittle. Mapping order is important: `FileClobberedError` must become `ESTALE`; existing errno values should not be overwritten. Panic handling logs fatal, which can terminate process behavior rather than returning an error.

Test signals: companion tests cover gRPC permission/already-exists/not-found/canceled/unauthenticated, HTTP unauthorized, and file-clobbered to ESTALE.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/error_mapping.go -->
