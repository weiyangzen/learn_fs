# `sources/user-network-fs/go-fuse/internal/openat/openat.go`

## Purpose
Symlink-aware open helper rooted at a base directory.

## Important APIs, Types, And Functions
`OpenSymlinkAware` opens `baseDir` as a directory fd, rejects absolute relative paths, and calls platform `openatNoSymlinks`.

## Control Flow
`OpenSymlinkAware` opens `baseDir` as a directory fd, rejects absolute relative paths, and calls platform `openatNoSymlinks`.

## State And Persistence
State is only transient fds. Integration protects passthrough/loopback-style opens from symlink traversal. Risk is non-Linux fallback only blocks final component symlinks.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is only transient fds. Integration protects passthrough/loopback-style opens from symlink traversal. Risk is non-Linux fallback only blocks final component symlinks.

## Test Signals
State is only transient fds. Integration protects passthrough/loopback-style opens from symlink traversal. Risk is non-Linux fallback only blocks final component symlinks.
