# `sources/user-network-fs/go-fuse/fuse/pathfs/loopback_darwin.go`

## Purpose
Implements Darwin-specific path-based `loopbackFileSystem.Utimens` using `syscall.Utimes` because older macOS lacks `utimensat`/`UTIME_OMIT`.

## Important APIs, Types, And Functions
`Utimens` and `utimens.Fill` are the key APIs; it fetches attrs when either timestamp is nil, preserving the missing timestamp before calling host `Utimes`.

## Control Flow
`Utimens` and `utimens.Fill` are the key APIs; it fetches attrs when either timestamp is nil, preserving the missing timestamp before calling host `Utimes`.

## State And Persistence
The file persists only host filesystem timestamps and depends on `fuse.Attr`, `syscall`, and internal `utimens`. Risk is symlink behavior: `Utimes` follows paths, unlike Linux no-follow `utimensat`. The shared loopback utimens tests cover nil-atime/nil-mtime preservation.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
The file persists only host filesystem timestamps and depends on `fuse.Attr`, `syscall`, and internal `utimens`. Risk is symlink behavior: `Utimes` follows paths, unlike Linux no-follow `utimensat`. The shared loopback utimens tests cover nil-atime/nil-mtime preservation.

## Test Signals
The file persists only host filesystem timestamps and depends on `fuse.Attr`, `syscall`, and internal `utimens`. Risk is symlink behavior: `Utimes` follows paths, unlike Linux no-follow `utimensat`. The shared loopback utimens tests cover nil-atime/nil-mtime preservation.
