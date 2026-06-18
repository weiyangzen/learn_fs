# `sources/user-network-fs/go-fuse/fuse/types_linux.go`

## Purpose
Linux errno, capability, statfs, and statx helpers.

## Important APIs, Types, And Functions
Defines ENODATA/ENOATTR/EREMOTEIO, Linux-only capability bits, `FromStatfsT`, `InitOut.setFlags`, and `SxTime.FromStatxTimestamp`.

## Control Flow
Defines ENODATA/ENOATTR/EREMOTEIO, Linux-only capability bits, `FromStatfsT`, `InitOut.setFlags`, and `SxTime.FromStatxTimestamp`.

## State And Persistence
No active state. Integrated by INIT negotiation, statfs replies, xattr errors, and statx output. Risk is keeping Linux capability bits in sync with kernel headers.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No active state. Integrated by INIT negotiation, statfs replies, xattr errors, and statx output. Risk is keeping Linux capability bits in sync with kernel headers.

## Test Signals
No active state. Integrated by INIT negotiation, statfs replies, xattr errors, and statx output. Risk is keeping Linux capability bits in sync with kernel headers.
