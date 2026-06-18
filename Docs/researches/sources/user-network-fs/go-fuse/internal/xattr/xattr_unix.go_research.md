<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/xattr/xattr_unix.go -->
# sources/user-network-fs/go-fuse/internal/xattr/xattr_unix.go

## Purpose
Implements non-FreeBSD extended-attribute list parsing, where names are NUL-separated.

## Important APIs, Types, and Functions
`parseAttrNames` uses `bytes.Split(buf, []byte{0})`.

## Control Flow
There is no filtering; the split result is returned directly.

## State and Persistence Behavior
Stateless; returned slices alias the input buffer and may include a final empty name when the kernel buffer ends with NUL.

## Dependencies and Integration Points
Used by Linux, Darwin, and other Unix builds through `ParseAttrNames`.

## Risks and Edge Cases
A trailing empty attribute name can appear; callers must tolerate it. Embedded NULs are impossible in real xattr names but would be split if given synthetic data.

## Test Signals
Tests should include kernel `Listxattr` output and synthetic buffers with trailing NULs to document the empty-tail behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/xattr/xattr_unix.go -->
