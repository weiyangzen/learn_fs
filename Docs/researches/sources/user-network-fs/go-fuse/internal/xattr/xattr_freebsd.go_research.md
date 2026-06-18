<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/xattr/xattr_freebsd.go -->
# sources/user-network-fs/go-fuse/internal/xattr/xattr_freebsd.go

## Purpose
Implements FreeBSD/BSD extended-attribute name parsing, where each name is prefixed by a one-byte length.

## Important APIs, Types, and Functions
`parseAttrNames` walks the byte buffer and appends `buf[p:p+len]` entries.

## Control Flow
The loop reads a length byte, slices the following name bytes, appends the name, and advances until the buffer is exhausted.

## State and Persistence Behavior
Stateless; output names alias the input buffer.

## Dependencies and Integration Points
Selected on FreeBSD and used through `ParseAttrNames` by xattr tests and FUSE compatibility code.

## Risks and Edge Cases
Malformed buffers with a length exceeding remaining bytes will panic. The parser trusts kernel output, so it is unsuitable for untrusted arbitrary input without validation.

## Test Signals
FreeBSD tests should list multiple xattrs, including short and long names, and verify no Linux-style NUL splitting is assumed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/xattr/xattr_freebsd.go -->
