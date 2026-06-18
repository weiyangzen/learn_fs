# File Research: sources/virtualization/virtiofsd/src/passthrough/device_state/serialized.rs

This file defines the migration wire-format structs and enums for passthrough filesystem state. It intentionally contains data shapes only; conversion to bytes happens in `serialization.rs`, and restoration happens in `deserialization.rs`.

Wire format:
- `PassthroughFs`: versioned top-level enum with `V1` and `V2`.
- `PassthroughFsV1`: inodes, next inode ID, open handles, next handle ID, and negotiated FUSE options.
- `PassthroughFsV2`: wraps `V1` and adds `mount_paths` for file-handle migration.
- `NegotiatedOpts`: remembers `writeback`, `announce_submounts`, `posix_acl`, and supplementary group extension negotiation.

Inode representation:
- `Inode`: stores FUSE inode ID, refcount, `InodeLocation`, and optional verification `SerializableFileHandle`.
- `InodeLocation::RootNode`: destination finds root independently.
- `InodeLocation::Path { parent, filename }`: destination opens a filename relative to another serialized inode.
- `InodeLocation::FullPath { filename }`: destination opens a path relative to shared root without a parent strong reference.
- `InodeLocation::FileHandle { handle }`: destination opens by file handle using V2 mount-path translation.
- `InodeLocation::Invalid`: destination must apply `migration_on_error` policy or preserve guest-visible failure state.

Handle representation:
- `Handle`: handle ID, owning inode ID, and `HandleSource`.
- `HandleSource::OpenInode { flags }`: reopen the inode using original `openat(2)` flags.

Important compatibility detail:
- The top-level enum allows incompatible future changes by adding variants while retaining support for older streams.
- V2 is backward-compatible by embedding V1 and adding mount-path metadata needed only for file handles.

Interactions:
- Uses `SerializableFileHandle` from `file_handle.rs`.
- Type aliases align wire inode IDs and handle IDs with `inode_store::Inode` and `passthrough::Handle`.
- Consumed by both serializer and deserializer.

Edge cases and risks:
- Filename fields are UTF-8 `String`s, so non-UTF-8 host paths cannot be represented in path-based migration.
- V1 cannot carry mount path translations, so file-handle migration is meaningfully V2-only.
