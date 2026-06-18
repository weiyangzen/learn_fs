# `sources/user-network-fs/go-fuse/internal/access.go`

## Purpose
Implements permission checking used by loopback `Access`.

## Important APIs, Types, And Functions
`HasAccess` checks root, zero mask, owner bits, primary group bits, other bits, and supplementary groups via `os/user`.

## Control Flow
`HasAccess` checks root, zero mask, owner bits, primary group bits, other bits, and supplementary groups via `os/user`.

## State And Persistence
No persistent state; it queries OS user/group database on demand. Risks include expensive/fragile supplementary group lookup and simplified root semantics. Tests cover owner/group/other/root cases.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistent state; it queries OS user/group database on demand. Risks include expensive/fragile supplementary group lookup and simplified root semantics. Tests cover owner/group/other/root cases.

## Test Signals
No persistent state; it queries OS user/group database on demand. Risks include expensive/fragile supplementary group lookup and simplified root semantics. Tests cover owner/group/other/root cases.
