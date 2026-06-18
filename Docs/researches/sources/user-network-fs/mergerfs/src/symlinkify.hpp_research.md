# sources/user-network-fs/mergerfs/src/symlinkify.hpp

## Purpose
Implements helper logic for representing old, immutable regular files as symlinks in stat results.

## Important APIs, Types, and Functions
`can_be_symlink()` overloads inspect `struct stat` or `fuse_statx`; `convert()` overloads rewrite mode, size, and block count; `convert_if_can_be_symlink()` applies conversion when timeout and metadata conditions permit.

## Control Flow
A file cannot be symlinkified if it is a directory or has any write bit. The helper compares current time against mtime and ctime using the configured timeout. Conversion changes type to `S_IFLNK`, permissions to `0777`, size to target length, and blocks to zero.

## State and Persistence Behavior
No on-disk file is changed; only caller-provided stat buffers are mutated.

## Dependencies and Integration Points
Depends on FUSE stat types, base integer types, POSIX mode macros, and time. It integrates with getattr/statx presentation paths.

## Risks and Edge Cases
Time comparisons use seconds and can be sensitive to clock changes. Permission-bit checks do not consider ACLs. Mutating metadata can surprise applications expecting backing-file type.

## Test Signals
Test writable, directory, old/new ctime/mtime, negative timeout, stat and statx overloads, and readlink/getattr integration.
