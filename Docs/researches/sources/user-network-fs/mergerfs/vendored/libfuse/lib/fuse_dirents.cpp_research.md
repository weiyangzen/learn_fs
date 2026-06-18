# sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_dirents.cpp

## Purpose
`fuse_dirents.cpp` builds packed FUSE directory-entry buffers and an offset index used by the high-level readdir cache in `fuse.cpp`.

## Important APIs, Types, and Functions
The exported API is `fuse_dirents_init`, `fuse_dirents_add` for POSIX `dirent`, `fuse_dirents_add` for mergerfs `fs::dirent64`, `fuse_dirents_reset`, and `fuse_dirents_free`. Internal helpers calculate aligned `fuse_dirent_t` sizes, grow the kvec-backed byte buffer, and allocate space for the next entry.

## Control Flow
Initialization allocates a 32 KiB data buffer and an offset vector with an initial zero entry. Each add operation computes aligned entry size, resizes the data vector when needed, appends an offset entry, fills inode/name/type fields, and copies the name bytes without appending a string terminator. `fuse_lib_readdir` later uses the offset vector as the FUSE directory offset space.

## State and Persistence
The `fuse_dirents_t` object owns two dynamic kvec buffers: raw packed dirent bytes and `uint32_t` offsets. State is per open directory handle and is destroyed on releasedir. It is not persistent and must be protected by the directory handle lock in the caller.

## Dependencies and Integration Points
This file depends on FUSE dirent structs, `kvec.h`, `fs_dirent64.hpp`, and C dirent/stat headers. `fuse.cpp` owns the lifecycle in `fuse_lib_opendir`, repopulates it through filesystem `readdir`/`readdir_plus`, and slices it for replies.

## Risks
Offsets are stored as `uint32_t`, so extremely large directory buffers risk truncation. Name length correctness is delegated to callers. Allocation failure must be propagated or the directory stream will return ENOMEM. Alignment must match kernel expectations for `fuse_dirent_t`.

## Test Signals
Test empty directories, many entries beyond 32 KiB, long names, `dirent` and `dirent64` inputs, reset/reuse after repeated offset-zero reads, and ENOMEM simulation around buffer growth.
