# File Research: sources/os/linux/linux/fs/verity/read_metadata.c

## Purpose
Implements `FS_IOC_READ_VERITY_METADATA`, allowing userspace to read the Merkle tree byte stream, descriptor, or builtin signature of a verity file.

## Main Functions
- `fsverity_read_merkle_tree()`: copies a requested Merkle tree byte range to userspace, with optional readahead.
- `fsverity_read_buffer()`: bounded copy from a kernel buffer to userspace.
- `fsverity_read_descriptor()`: loads descriptor, strips builtin signature, zeroes `sig_size`, and returns descriptor bytes.
- `fsverity_read_signature()`: returns builtin signature bytes or `-ENODATA`.
- `fsverity_ioctl_read_metadata()`: validates arguments, bounds length to `INT_MAX`, dispatches by metadata type.

## Important Design Points
- Merkle tree metadata is exposed as a byte stream, independent of Merkle block size.
- Readahead is issued over the requested page range when filesystem provides `readahead_merkle_tree`.
- Descriptor metadata intentionally excludes the builtin signature.
- Offset plus length overflow is rejected.

## Cross-File Relationships
- Uses cached `fsverity_info` from `open.c`.
- Uses filesystem `read_merkle_tree_page()` and optional `readahead_merkle_tree()` operations.
- Uses `fsverity_get_descriptor()` from `open.c`.

## Risks / Review Notes
- Copy loop must release mapped pages on all error paths.
- Return value is byte count read, 0 on EOF, or negative errno; partial reads take precedence over later errors.
- Metadata exposure must preserve exact descriptor/signature separation.
