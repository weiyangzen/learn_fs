# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_resize_volume.c

## Role

Implements `-S/--volume-size` and trailing resize size handling. It grows an OCFS2 filesystem online via kernel ioctls or offline by directly updating allocation metadata. Shrinking is explicitly unsupported.

## Size Parsing

`resize_volume_parse_option()` accepts an optional unit prefix stored by `ocfs2ne.c`:

- `bytes:`
- `blocks:`
- `clusters:`

If no size is supplied, `rs_size` remains zero and later means grow to device capacity.

`resize_volume_run()` converts the stored unit into bytes using superblock block/cluster size bits, handles wrap by saturating to `UINT64_MAX`, then calls `update_volume_size()`.

## Validation

`check_new_size()` enforces:

- requested size cannot exceed `UINT32_MAX` clusters
- requested clusters must fit the device
- requested clusters cannot be less than current filesystem clusters
- if journal block64 is not enabled, target block count must not exceed `UINT32_MAX`

If size is zero, it derives target clusters from current device size.

## Offline Growth

`update_volume_size_offline()` sets `OCFS2_FEATURE_INCOMPAT_RESIZE_INPROG`, calls `run_resize()`, clears the in-progress flag, and writes the superblock.

`run_resize()` reads the global bitmap inode, extends the tail group if possible, creates new group descriptors, updates chain records, updates bitmap totals, grows `i_clusters` / `i_size`, and updates filesystem cluster/block counts.

`init_new_gd()` initializes new cluster groups, zeroes the first cluster in each group, reserves backup superblock clusters when needed, links groups into chain records, and writes descriptors.

## Online Growth

`update_volume_size_online()` takes a DLM lock named `tunefs-online-resize-lock`, calls `run_resize(..., online=1)`, then unlocks.

For online changes:

- tail extension uses `OCFS2_IOC_GROUP_EXTEND`
- new groups use `OCFS2_IOC_GROUP_ADD`
- group descriptors are prepared by userspace but linked by kernel ioctls

## Backup Superblock Handling

`reserve_backup_in_group()` checks whether backup-super support is enabled and reserves clusters corresponding to backup superblock offsets inside newly added groups.

## Open Flags

Declared as `TUNEFS_FLAG_RW | TUNEFS_FLAG_ALLOCATION | TUNEFS_FLAG_ONLINE`.

## Notable Risks

- This is high-blast-radius metadata code: it modifies global bitmap, chain records, group descriptors, superblock state, and filesystem size counters.
- Error recovery relies heavily on the resize in-progress flag for offline operations.
- Online and offline paths share `run_resize()` but differ in who commits linkage; maintaining invariant parity is subtle.
