# sources/user-network-fs/bazil-fuse/protocol.go

Purpose: `protocol.go` defines a simple FUSE protocol version type and feature predicate helpers.

Important APIs, types, and functions: `Protocol{Major, Minor}` implements `String`, `LT`, and `GE`. Deprecated feature predicates `HasAttrBlockSize`, `HasReadWriteFlags`, `HasGetattrFlags`, `HasOpenNonSeekable`, `HasUmask`, and `HasInvalidate` now always return true because the package minimum protocol supports them. `HasNotifyDelete` returns true for protocol >= 7.18.

Control flow: Version comparison is lexicographic by major then minor. Feature helpers are direct boolean returns.

State and persistence behavior: Stateless value type.

Dependencies and integration points: Used in `fuse.go` init negotiation and in kernel struct size/version gating from `fuse_kernel.go`.

Risks: Deprecated helpers may give callers a false sense that runtime negotiation still varies for those features. `HasNotifyDelete` remains version-sensitive and should be checked by code using delete notifications.

Test signals: No direct test in this subset, but `fuse.go` and integration tests exercise negotiated protocol behavior.
