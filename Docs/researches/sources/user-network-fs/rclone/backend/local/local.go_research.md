
# sources/user-network-fs/rclone/backend/local/local.go

## Purpose
Implements rclone's local disk backend, mapping local files, directories, symlinks, metadata, hashes, streaming, and moves into rclone filesystem interfaces.

## Important APIs, Types, And Control Flow
Key types are `Options`, `Fs`, `Object`, `Directory`, `localOpenFile`, and the `timeType` enum. Registration exposes many backend flags: symlink handling, Unicode normalization, update checking, one-file-system, case sensitivity, cloning, preallocation, sparse writes, modtime disabling, fatal ENOSPC, time type, hashes, and encoding. `NewFs` parses options, rejects conflicting symlink modes, cleans roots, sets features, chooses `os.Stat` vs `os.Lstat`, detects root files and translated links, and stores root device for one-filesystem filtering. `List` handles platform directory reads, filtering, symlink following/translation, device boundary checks, special-file skips, and invalid UTF-8 warnings. Object methods handle hash caching, update-change detection, range reads, symlink-as-file translation, writes with preallocation/hash options, metadata writes, random-access writers, removal, and root path cleaning.

## State And Persistence
Persistent state is the local filesystem itself: files, directories, symlinks, times, modes, ownership, xattrs, and optional sparse/preallocated extents. Runtime state includes cached metadata/hashes guarded by `objectMetaMu`, warning deduplication, detected precision, root device, and xattr support flag.

## Dependencies And Integration Points
Uses rclone `fs`, accounting, filter, fserrors, hash, operations expectations, encoder, file helpers, and readers. OS-specific helpers provide `About`, copy clone, device IDs, metadata, xattrs, symlink errors, removal, and time setters. Implements many optional interfaces including put streaming, mover, dir mover, commander, writer-at, dir modtime, mkdir metadata, metadata, and set metadata.

## Risks And Test Signals
Risks include races with changing files, stale hash cache, partial-write cleanup, ENOSPC fatal wrapping, Windows hidden-file handling, symlink security isolation, filter-aware error suppression, one-filesystem device filtering, path encoding/UNC normalization, preallocation side effects, sparse warnings, and platform metadata disparities. Tests cover update detection, symlink modes, metadata/xattrs, filtering, copy links, hash cache invalidation, disk-full fatal behavior, remove retry, Windows cleanup, and generic local integration.
