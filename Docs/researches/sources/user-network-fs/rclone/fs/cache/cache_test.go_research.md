# sources/user-network-fs/rclone/fs/cache/cache_test.go

Purpose: tests the fs cache using a mock backend factory to verify canonicalization, file-parent caching, error handling, pinning, and clearing.

Important APIs/functions: `mockNewFs` returns `mockfs.NewFs` for directories, parent `Fs` plus `fs.ErrorIsFile` for file paths, or a sentinel error. Tests include `TestGet`, `TestGetFile`, `TestGetFile2`, `TestGetError`, `TestPutErr`, `TestPut`, `TestPin`, `TestPinFile`, `TestClearConfig`, `TestClear`, and `TestEntries`.

Control flow: most tests call `GetFn` with a deterministic factory and assert the factory is only called on cache misses. File tests first resolve a child path, then resolve the same child and parent path to confirm they all share one cached `Fs` while child lookups retain `fs.ErrorIsFile`.

State and persistence behavior: tests call `Clear` via cleanup and sometimes `ClearMappings` explicitly because package state is global. `TestPinFile` inspects `childParentMap` length and `EntriesWithPinCount` to verify pinning a child and parent affects the same cache entry.

Dependencies and integration points: uses `mockfs`, `fs.ErrorIsFile`, and `testify`. It constrains behavior relied on by all rclone operations using cached remotes.

Risks: tests use package globals (`called`, maps) and therefore require cleanup discipline. They do not exercise cache expiration timers, finalizer shutdown, rc job pin hooks, or concurrent access.

Test signals: good coverage for canonical cache semantics and file-vs-directory error preservation.
