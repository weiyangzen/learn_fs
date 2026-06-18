# sources/sync-backup/git-lfs/lfs/scanner.go

Purpose: Defines common scanner constants, pointer result wrappers, and channel wrapper types used by Git LFS scanning pipelines.

Important APIs/types/functions: `blobSizeCutoff`, `stdoutBufSize`, `chanBufSize`, `WrappedPointer`, `catFileBatchCheck`, `catFileBatch`, `PointerChannelWrapper`, `StringChannelWrapper`, `TreeBlobChannelWrapper`, and their constructors.

Control flow: `catFileBatchCheck` creates small-revision, lockable, and error channels, delegates process setup to `runCatFileBatchCheck`, then returns a string wrapper and lockable channel. `catFileBatch` similarly prepares pointer and lockable channels, calls `runCatFileBatch`, and returns a pointer wrapper.

State and persistence behavior: No disk persistence. State is asynchronous and channel-based. Error channels are deliberately buffered to avoid goroutine blockage while scan consumers drain result channels and later call `Wait`.

Dependencies and integration points: Depends on `config.Environment`, `git.TreeBlob`, and `tools.BaseChannelWrapper`. The delegated `runCatFileBatch*` functions are the integration point with object database and Git cat-file behavior.

Risks and edge cases: Channel buffer sizes and error-channel capacities are correctness-sensitive; undersized buffers could deadlock if producers emit more errors than expected. `blobSizeCutoff` limits pointer scanning to small blobs, so changing pointer format size assumptions affects scanning.

Test signals: Direct tests are elsewhere; `scanner_test.go` and `scanner_git_test.go` validate scanner behavior through log parsing and repository scenarios.
