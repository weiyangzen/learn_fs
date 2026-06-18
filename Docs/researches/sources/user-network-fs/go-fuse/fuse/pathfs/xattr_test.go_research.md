# `sources/user-network-fs/go-fuse/fuse/pathfs/xattr_test.go`

## Purpose
Linux pathfs xattr integration tests using a synthetic filesystem with in-memory xattr maps.

## Important APIs, Types, And Functions
Defines `XAttrTestFs`, `NewXAttrFs`, xattr method overrides, `xattrTestCase`, and tests for empty attrs, missing attrs, reading, writing, listing, and removing xattrs.

## Control Flow
Defines `XAttrTestFs`, `NewXAttrFs`, xattr method overrides, `xattrTestCase`, and tests for empty attrs, missing attrs, reading, writing, listing, and removing xattrs.

## State And Persistence
State is an in-memory `map[string][]byte`, copied on set to avoid aliasing. It integrates through pathfs/nodefs mount and Linux helper calls. Risks include unordered list results and Linux-only xattr namespace behavior.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is an in-memory `map[string][]byte`, copied on set to avoid aliasing. It integrates through pathfs/nodefs mount and Linux helper calls. Risks include unordered list results and Linux-only xattr namespace behavior.

## Test Signals
State is an in-memory `map[string][]byte`, copied on set to avoid aliasing. It integrates through pathfs/nodefs mount and Linux helper calls. Risks include unordered list results and Linux-only xattr namespace behavior.
