# `sources/user-network-fs/go-fuse/fuse/print_freebsd.go`

## Purpose
FreeBSD-specific printer initialization.

## Important APIs, Types, And Functions
`init` registers `CAP_NO_OPENDIR_SUPPORT` so init capability debug output can name it.

## Control Flow
`init` registers `CAP_NO_OPENDIR_SUPPORT` so init capability debug output can name it.

## State And Persistence
No state beyond global flag table mutation. Risk is limited to debug readability; functional protocol behavior is elsewhere.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No state beyond global flag table mutation. Risk is limited to debug readability; functional protocol behavior is elsewhere.

## Test Signals
No state beyond global flag table mutation. Risk is limited to debug readability; functional protocol behavior is elsewhere.
