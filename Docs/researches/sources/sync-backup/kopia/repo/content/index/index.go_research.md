# sources/sync-backup/kopia/repo/content/index/index.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/index.go_research.md`.

Purpose: declares the read-only pack index abstraction and dispatches byte buffers to the correct binary index version implementation.

Important APIs: `Index` combines `io.Closer`, `ApproximateCount`, `GetInfo`, and range `Iterate`. `Open` first reads a v1-compatible header, then dispatches to `openV1PackIndex` or `openV2PackIndex`. `safeSlice` and `safeSliceString` wrap slice operations and convert panics from corrupt offsets or lengths into errors.

Control flow: index opening validates the header version and passes encryptor overhead to v1 because v1 does not persist original content length. Both v1 and v2 implementations use `safeSlice` during binary search and entry decoding.

State and persistence behavior: `Index` is immutable over a byte buffer and optional closer. It represents one index blob or local pack index; merged repository views are implemented separately by `Merged`.

Dependencies and integration: depends on hashing constants, errors, and lower-level index versions. Used by content index parsing, pack recovery, index blob loading, tests, and merged committed indexes.

Risks and tests: corrupt index bytes must not panic; `safeSlice` is the defensive boundary. Version dispatch must remain backward-compatible. Pack index tests open both versions, fuzz mutated bytes, and verify lookup and iteration behavior.
