# sources/user-network-fs/rclone/backend/chunker/chunker_internal_test.go

## Purpose
This file provides chunker-specific internal tests beyond rclone's generic backend suite. It directly exercises unexported format parsing, object internals, transaction behavior, metadata safety, corruption prevention, and server-side move cases.

## Important APIs, Types, And Control Flow
`InternalTest` dispatches named subtests. `testChunkNameFormat` validates accepted and rejected name patterns, generated printf formats, regexes, data/control chunk names, temporary suffixes, old-style suffix parsing, and panic paths. `testSmallFileInternals` checks how small and empty files are represented under metadata-none, hash-all, and normal modes. `testPreventCorruption` ensures chunk-looking paths cannot be created, updated, moved, copied, or removed when that would corrupt a composite file. Other tests cover chunk number overflow, user content that resembles metadata, future metadata versions, rename/norename backwards compatibility, server-side move between differently configured derived chunker remotes, and `md5all` metadata creation on slow-hash bases.

## State And Persistence
Tests create files and chunks on the wrapped base remote, frequently bypassing chunker to simulate corrupt, legacy, or future states. They mutate `f.opt`, `f.useNoRename`, and chunk size directly, then restore them in defers. Cleanup uses `operations.Purge` on test directories.

## Dependencies And Integration Points
The file uses `fstests`, `fstest`, `operations`, `object.NewStaticObjectInfo`, config-derived remotes via `deriveFs`, random content, and `hash` checks. It is compiled inside package `chunker` so it can inspect unexported fields and methods.

## Risks And Test Signals
Signals are highly targeted: strict chunk-name contract, fail-hard behavior, safe handling of future metadata, refusal to update unsupported objects, compatibility from old rename chunks to new norename scanning, and correct metadata/hash behavior. Risks include tests depending on direct internal mutation and small chunk sizes, plus branch coverage that varies with wrapped backend features.
