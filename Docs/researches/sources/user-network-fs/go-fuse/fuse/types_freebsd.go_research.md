# `sources/user-network-fs/go-fuse/fuse/types_freebsd.go`

## Purpose
FreeBSD errno, capability, statfs, and init flag definitions.

## Important APIs, Types, And Functions
Defines ENOATTR/ENODATA aliases, `CAP_NO_OPENDIR_SUPPORT`, unsupported capability zeros, `FromStatfsT`, and `setFlags`.

## Control Flow
Defines ENOATTR/ENODATA aliases, `CAP_NO_OPENDIR_SUPPORT`, unsupported capability zeros, `FromStatfsT`, and `setFlags`.

## State And Persistence
No active state. Risk is FreeBSD kernel header drift and correct signed/unsigned statfs field conversion.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No active state. Risk is FreeBSD kernel header drift and correct signed/unsigned statfs field conversion.

## Test Signals
No active state. Risk is FreeBSD kernel header drift and correct signed/unsigned statfs field conversion.
