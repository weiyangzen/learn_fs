<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/core.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/core.go

## Purpose

This file defines `Core`, the compact pre-inode description used throughout gcsfuse to represent a file, directory, folder, local pending file, implicit directory, or missing lookup result before constructing or returning a full inode.

## Important APIs, Types, and Functions

`Core` contains `FullName Name`, optional `Bucket *gcsx.SyncerBucket`, optional `MinObject *gcs.MinObject`, optional HNS `Folder *gcs.Folder`, and `Local bool`. `Exists` reports whether the pointer receiver is non-nil. `Type` maps the core to `metadata.Type`: nil is unknown, no object/folder/local with a directory name is implicit directory, directory names are explicit directory, symlink metadata is symlink, and all else is regular file. `SanityCheck` verifies folder/object names match `FullName` and that non-local file names have backing objects.

## Control Flow

Lookup/listing code constructs `Core` values from stat, list, folder, or local state. Higher layers inspect `Type()` to choose FUSE dirent type, inode type, cache insertion, and conflict behavior. `SanityCheck` is a guard against inconsistent metadata before using a core.

## State and Persistence Behavior

`Core` has no owned persistence. It references bucket/object/folder metadata supplied by storage or local inode state. A nil `*Core` is the canonical nonexistence representation.

## Dependencies and Integration Points

It integrates `internal/cache/metadata`, `gcsx.SyncerBucket`, `gcs.MinObject`, `gcs.Folder`, and name/symlink helpers in the inode package. It is a central data contract between directory lookup/listing, file/dir inode construction, and metadata caches.

## Risks and Edge Cases

Type precedence matters: HNS folders and object-backed directory names are explicit directories; local objectless file cores are regular files; objectless non-local file names are invalid. `Exists` on a nil pointer is intentionally safe because methods with pointer receivers can be called on nil in Go, but `SanityCheck` uses a value receiver and requires a real value.

## Test Signals

The paired tests verify file, local file, explicit directory, implicit directory, bucket root, nil nonexistent type, sanity-check mismatches, missing object errors, HNS folder sanity, and folder explicit-directory type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/core.go -->
