<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_common_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_common_test.go

Purpose: shared stale file handle integration tests and helpers for non-streaming writes. It verifies ESTALE when an open file is clobbered remotely, and no error when an unlinked local handle is synced/closed after local deletion.

Important APIs/types/functions: suite `staleFileHandleCommon`; `commonServerConfig`; helpers `clobberFile`, `createGCSObject`; tests `TestClobberedFileSyncAndCloseThrowsStaleFileHandleError` and `TestFileDeletedLocallySyncAndCloseDoNotThrowError`.

Control flow: setup disables metadata cache TTL to force fresh generation checks. Tests dirty `t.f1`, replace or remove the backing object, then sync/close and validate either `ESTALE` or success depending on local deletion semantics.

State and persistence behavior: fake GCS object generation/content is the persistent state. Open file handle state tracks the original generation and dirty local content. Clobbering must prevent unsynced data from overwriting the newer object.

Dependencies and integration points: uses storage utilities and integration `operations` helpers for ESTALE, no-file, close, and object-not-found validation. Exercises file sync/flush generation preconditions.

Risks: stale-handle correctness is central for data safety. The sync path must distinguish remote clobber/delete from a file intentionally unlinked through the same mount while the handle remains open.

Test signals: clobbered dirty file returns ESTALE on sync and close and preserves remote content; locally deleted open file can still be written, synced, and closed without resurrecting the object.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_common_test.go -->
