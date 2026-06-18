# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/xattr.c

This file implements fsck validation and repair for OCFS2 extended attributes stored inline in inodes, in external xattr blocks, and in indexed xattr buckets.

Key structures and helpers:
- Defines xattr locations `IN_INODE`, `IN_BLOCK`, and `IN_BUCKET`, with `xattr_info` carrying location, max valid offset, and block number for diagnostics.
- Uses `used_area` and `used_map` to track occupied header, entry, and name/value regions while validating xattr layout.
- `check_xattr_count()` detects plausible entry count from terminators, bucket hash ordering, and object size limits, then optionally fixes `xh_count`.
- `check_xattr_entry()` validates entry placement, name offsets, local-vs-external value sizing, name/value overlap, and name hash correctness; bad entries are compacted out of the header.
- `check_xattr_value()` verifies extent lists for non-local xattr values through shared extent-checking callbacks.

Control flow:
- `check_xattr()` runs count, entry, external-value, and bucket-only free-space metadata checks.
- `ocfs2_check_xattr_buckets()` reads a run of xattr buckets, detects or fixes bucket count, validates each bucket, and writes changed buckets.
- `o2fsck_check_xattr_index_block()` validates indexed xattr extent records, writes the root if changed, then walks bucket records via `ocfs2_xattr_get_rec()`.
- `o2fsck_check_xattr_block()` validates the external xattr block signature, then dispatches to inline block-header checking or indexed checking.
- `o2fsck_check_xattr_ibody()` locates inline xattr storage at the end of the inode block.
- Public entry `o2fsck_check_xattr()` is gated by `OCFS2_HAS_XATTR_FL`, handles inline xattrs first, writes changed inodes, then checks `i_xattr_loc`.

Integration notes:
- Depends on libocfs2 xattr helpers, fsck prompt/problem infrastructure, and `check_el()` from extent validation.
- Repairs are interactive via `prompt()` and mark buffers dirty through local `changed` flags.
- Important correctness concern: layout validation is defensive but manually manages offset arithmetic and list allocation; bad repair choices can leave stale name/value data intentionally in place while compacting only entries.
