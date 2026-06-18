# File Research: sources/local-fs/xfsprogs/libxfs/xfs_attr_leaf.h

## Purpose

`xfs_attr_leaf.h` declares the in-core attr leaf header and the shortform/leaf helper APIs used by the higher-level attr state machine and da btree code.

## Key Contents

`struct xfs_attr3_icleaf_hdr` is the normalized in-core representation of both legacy and CRC-enabled attr leaf headers. It contains sibling links, magic, entry count, used bytes, widened `firstused`, hole flag, and three free-map records.

The header exposes shortform helpers, shortform verification and fork removal, leaf-to-node and leaf-to-shortform conversion, `INCOMPLETE` flag manipulation, leaf split/add/remove/lookup/getvalue/list functions, shrink/unbalance helpers, hash/order utilities, entry-size calculation, buffer read, header conversion, and owner/header checks.

## Dependencies and Risks

Callers must provide initialized `xfs_da_args`, inode, transaction, geometry, and owner context consistent with the attr fork. The key invariant is that the widened in-core `firstused` must be converted correctly for 64 KiB blocks and that callers respect the lookup convention and stateful mutation of `args` fields.
