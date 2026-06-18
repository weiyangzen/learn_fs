# `sources/user-network-fs/go-fuse/internal/utimens/utimens_darwin.go`

## Purpose
Darwin timestamp helper for preserving omitted atime/mtime.

## Important APIs, Types, And Functions
Defines `timeToTimeval` and `Fill`; nil timestamps are filled from `fuse.Attr`, then converted to `syscall.Timeval`.

## Control Flow
Defines `timeToTimeval` and `Fill`; nil timestamps are filled from `fuse.Attr`, then converted to `syscall.Timeval`.

## State And Persistence
State is returned timeval slice only. Risk is pre-1970 conversion and attr requirement when either timestamp is nil. Used by pathfs loopback Darwin.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is returned timeval slice only. Risk is pre-1970 conversion and attr requirement when either timestamp is nil. Used by pathfs loopback Darwin.

## Test Signals
State is returned timeval slice only. Risk is pre-1970 conversion and attr requirement when either timestamp is nil. Used by pathfs loopback Darwin.
