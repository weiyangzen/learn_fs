# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/attr.c

## Purpose
Scrubs extended attribute metadata for an inode. It checks shortform and leaf/block attribute structures, verifies space accounting inside attr blocks, validates names/flags/parent-pointer values, and confirms each attribute can be looked up by hash and value retrieval.

## Main Entry Points
- `xchk_setup_xattr`: prepares repair tempfile if needed, allocates larger buffers for retry, then sets up inode content scrub.
- `xchk_setup_xattr_buf`: allocates reusable used/free bitmaps, name buffer, and value buffer.
- `xchk_xattr`: top-level xattr scrub for shortform or dabtree-backed attributes.
- `xchk_xattr_set_map`: bitmap helper for detecting byte-range overlap/out-of-range within attr blocks or shortform data.

## Key Behavior
For every listed xattr, `xchk_xattr_actor` validates ondisk flags, incomplete state, name validity, parent-pointer value format, allocates enough scratch value space, and performs `xfs_attr_get_ilocked` after setting the attr hash. Lookup returning `-ENODATA` is treated as corruption.

Leaf block scrub tracks used bytes and free bytes with bitmaps. It validates header padding, empty leaf handling, header bounds, entry table placement, hash ordering, name/value entry bounds, duplicate byte usage, freemap conflicts, zero-length freemap preen cases, and `usedbytes`.

Shortform scrub checks entry iteration bounds, valid namespace-only flags, and non-overlapping ranges for entry headers, names, and values.

## Dependencies and Interactions
Uses XFS da btree scrub, attr leaf/shortform helpers, parent pointer validation, listxattr walking, and shared attr repair buffer state declared in `attr.h`.

## Failure Handling
Memory pressure while growing the attr value buffer returns `-EDEADLOCK` to trigger a retry with maximum buffer allocation. Structural corruption generally sets fork-block corruption and may stop further block processing. Incomplete attrs are preen candidates, not hard corruption.
