
# sources/user-network-fs/rclone/backend/local/xattr_unsupported.go

## Purpose
Provides no-op xattr support for OpenBSD and Plan 9 where `pkg/xattr` is unavailable.

## Important APIs, Types, And Control Flow
Sets `xattrSupported = false`; `getXattr` and `setXattr` return nil without reading or writing metadata.

## State And Persistence
No xattr metadata is persisted.

## Dependencies And Integration Points
Keeps local metadata APIs compilable while feature flags report user metadata support as unavailable.

## Risks And Test Signals
The expected behavior is graceful absence of user metadata. Tests should assert feature flags and skip xattr round trips on these platforms.
