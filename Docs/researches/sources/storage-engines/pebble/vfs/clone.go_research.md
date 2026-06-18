# Research: sources/storage-engines/pebble/vfs/clone.go

## Purpose
`vfs/clone.go` implements recursive filesystem cloning between `vfs.FS` implementations. It supports optional skipping, syncing, and hardlink-or-copy optimization.

## Important APIs, Types, And Functions
`CloneOption` configures `cloneOpts`. Public options are `CloneSkip`, `CloneSync`, and `CloneTryLink`. `Clone(srcFS, dstFS, srcPath, dstPath, opts...)` returns `(true,nil)` on success, `(false,nil)` if the source does not exist, and `(false,err)` on real errors.

## Control Flow
`Clone` opens the source path and stats it. If it is a directory, it creates the destination directory, lists and sorts entries, recursively clones each non-skipped child, optionally syncs the destination directory, and returns. If it is a file and `CloneTryLink` is set with the same FS object, it tries `LinkOrCopy`. Otherwise it reads the full source file into memory, creates the destination file, writes all bytes, optionally syncs the file, closes it, and returns.

## State And Persistence
The function persists copied directory structure and file contents in the destination FS. `CloneSync` adds file and directory syncs for durability. It does not preserve metadata beyond directory/file existence and bytes.

## Dependencies And Integration Points
It depends on the `vfs.FS` and `vfs.File` interfaces, `io.ReadAll`, sorted directory listings, and `LinkOrCopy`. It is useful for checkpointing, test setup, and copying DB-like directory trees between VFS implementations.

## Risks And Edge Cases
Reading whole files into memory can be expensive for large files. If a source disappears during cloning, initial open returns `(false,nil)` for not-exist, while later recursive errors abort. `CloneTryLink` only attempts hardlinking when `srcFS == dstFS`; wrappers may prevent that identity check from matching. Syncing errors abort the clone.

## Test Signals
Tests should cover missing sources, nested directory copies, deterministic traversal, skip predicates, file contents, same-FS hardlink fallback, cross-FS copy fallback, file sync and directory sync paths, and mid-copy error propagation.
