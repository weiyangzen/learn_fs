# `sources/user-network-fs/go-fuse/fuse/types_unix.go`

## Purpose
Shared non-Darwin wire layout definitions for `Attr` and `SetAttrIn`.

## Important APIs, Types, And Functions
Defines Unix `Attr` fields and embeds `SetAttrInCommon` in `SetAttrIn`.

## Control Flow
Defines Unix `Attr` fields and embeds `SetAttrInCommon` in `SetAttrIn`.

## State And Persistence
State is protocol struct layout only. Risk is platform-specific padding/field mismatch; Linux/FreeBSD build tags combine this with per-OS constants.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is protocol struct layout only. Risk is platform-specific padding/field mismatch; Linux/FreeBSD build tags combine this with per-OS constants.

## Test Signals
State is protocol struct layout only. Risk is platform-specific padding/field mismatch; Linux/FreeBSD build tags combine this with per-OS constants.
