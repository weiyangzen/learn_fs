# `sources/user-network-fs/go-fuse/internal/renameat/renameat.go`

## Purpose
Cross-platform renameat wrapper.

## Important APIs, Types, And Functions
Exports `Renameat(olddirfd, oldpath, newdirfd, newpath, flags)` and delegates to platform implementation.

## Control Flow
Exports `Renameat(olddirfd, oldpath, newdirfd, newpath, flags)` and delegates to platform implementation.

## State And Persistence
Persistent effect is filesystem rename/exchange. Integrated by FUSE rename handling needing flags. Risk is platform flag support mismatch.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
Persistent effect is filesystem rename/exchange. Integrated by FUSE rename handling needing flags. Risk is platform flag support mismatch.

## Test Signals
Persistent effect is filesystem rename/exchange. Integrated by FUSE rename handling needing flags. Risk is platform flag support mismatch.
