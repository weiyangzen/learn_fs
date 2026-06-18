# File Research: sources/local-fs/xfsprogs/libxfs/xfs_rtrefcount_btree.h

This header defines the realtime refcount btree interface and layout helpers for both in-memory inode roots and on-disk dinode roots.

`XFS_RTREFCOUNT_BLOCK_LEN` aliases the CRC long-btree header length, because refcount metadata exists only on CRC-enabled filesystems. The exported API includes cursor initialization/staging/commit, record capacity calculations, maxlevel computation, cursor cache init/destroy, reserve sizing, inode-format loading/flushing, disk conversion, and metadata inode creation.

The address helpers calculate record, key, and pointer positions in an in-memory btree block. Leaf blocks contain `struct xfs_refcount_rec` arrays; internal nodes contain keys and `xfs_rtrefcount_ptr_t` pointers. Separate helpers address the packed on-disk root format `struct xfs_rtrefcount_root`, where records/keys/pointers begin after the root header.

Root size helpers distinguish in-memory root space from on-disk root space. `xfs_rtrefcount_broot_space_calc` uses the CRC btree block header length, while `xfs_rtrefcount_droot_space_calc` uses the smaller dinode root header. These helpers are central to safe ifork allocation and verifier sizing in the `.c` file.

The header is also used by userspace code, as noted in comments around apparently unused address helpers. Any layout change here must stay synchronized with the on-disk format definitions in `xfs_format.h` and the conversion routines in `xfs_rtrefcount_btree.c`.
