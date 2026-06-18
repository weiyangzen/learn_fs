<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/xattr/xattr.go -->
# sources/user-network-fs/go-fuse/internal/xattr/xattr.go

## Purpose
Exports the package-level xattr list-name parser behind a stable public internal function.

## Important APIs, Types, and Functions
`ParseAttrNames` delegates to the platform-selected `parseAttrNames` implementation.

## Control Flow
Runtime flow is a single call through to either BSD length-prefixed parsing or Unix NUL-separated parsing.

## State and Persistence Behavior
Stateless; returns slices referencing the caller-provided buffer.

## Dependencies and Integration Points
Used by `posixtest.XAttr` after `unix.Listxattr`; integrates with platform files selected by build tags.

## Risks and Edge Cases
Callers must not mutate or discard the buffer before consuming returned names. Empty trailing names may appear on NUL-separated platforms.

## Test Signals
Xattr list tests should set an attribute, list names, parse the result, and find the expected name on Linux and BSD conventions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/xattr/xattr.go -->
