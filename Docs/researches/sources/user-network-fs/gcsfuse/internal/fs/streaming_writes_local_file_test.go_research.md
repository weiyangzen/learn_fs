<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/streaming_writes_local_file_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/streaming_writes_local_file_test.go

Purpose: runs streaming-write coverage for local-only files and adds a directory removal case involving local, empty, and non-empty objects.

Important APIs/types/functions: constant `fileName`; suite `StreamingWritesLocalFileTest`; setup enabling streaming writes and zero metadata TTL; test `TestRemoveDirectoryContainingLocalAndEmptyObject`.

Control flow: setup creates local-only `foo` with no GCS object. Inherited common tests cover unlink, rename, truncate, and out-of-order write behavior. The directory test creates an explicit directory with empty and non-empty objects, adds local and dirty empty-object handles, removes the directory recursively, closes handles, and validates all objects are gone.

State and persistence behavior: local file state transitions to streamed GCS data only when writes are finalized. Recursive directory removal must remove synced objects, empty-object handles, local-only files, and explicit directory object state.

Dependencies and integration points: uses `operations.CreateLocalFile`, fake object creation through `fsTest.createObjects`, direct I/O opens, streaming write config, and object-not-found validation.

Risks: recursive delete while files are open and dirty can leave GCS objects behind or cause close errors. Local-only and empty-object streaming paths must converge on the same cleanup semantics.

Test signals: inherited streaming write suite plus successful `RemoveAll` of a directory containing local dirty file, empty dirty object, non-empty object, and explicit directory marker, with all GCS objects absent after closes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/streaming_writes_local_file_test.go -->
