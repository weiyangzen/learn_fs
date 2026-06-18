# sources/sync-backup/syncthing/lib/fs/fakefs.go

## Purpose
Provides an in-memory, deterministic filesystem for tests and benchmarks. Metadata is stored in memory, contents can be generated pseudo-randomly from file names or stored explicitly, and optional case-insensitive behavior mimics Windows/macOS.

## Important APIs, Types, and Functions
Registers `FilesystemTypeFake`. Core types are `fakeFS`, `fakeEntry`, `fakeFile`, and `fakeFileInfo`. Implements most `Filesystem` operations, `PlatformData`, metrics counters, and fake content reads via `readShortAt`.

## Control Flow
`newFakeFilesystem` parses query parameters, reuses roots from a global cache, optionally populates random files, and creates `.stfolder` unless disabled. Operations lock `fs.mut`, find entries via path components, and mutate in-memory trees. Reads either return stored `content` or deterministic random blocks seeded by file name and block number. `NewFilesystem` wraps fakeFS with walk/case/mtime layers as requested.

## State and Persistence Behavior
Persistent only for process lifetime: `fakeFSCache` maps root URI to shared fake trees. File writes update size and optional content, but default fake content is generated rather than stored. Ownership, modtime, mode, symlink destination, and child maps are stored per entry.

## Dependencies and Integration Points
Used heavily by fs tests, benchmarks, case conflict detection, and mtime tests. Integrates with `unixPlatformData` for ownership/xattr-shaped metadata.

## Risks
`RemoveAll` increments its counter twice. `Walk` is not implemented directly and relies on `NewWalkFilesystem` wrapping. `SameFile` is approximate and can false-positive. `ReadAt` comments note it affects internal offset despite Go's usual contract.

## Test Signals
`fakefs_test.go` covers sensitive/insensitive operations, deterministic reads, content mode, symlinks, rename/remove semantics, `SameFile`, and name presentation.
