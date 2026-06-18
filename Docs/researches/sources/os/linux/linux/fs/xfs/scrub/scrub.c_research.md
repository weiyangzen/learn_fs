# File Research: sources/os/linux/linux/fs/xfs/scrub/scrub.c

This is the central online scrub and repair dispatcher for XFS. It validates ioctl inputs, maps scrub type numbers to setup/scrub/repair callbacks, manages scrub context lifetime, records health and stats, implements retry modes, and exposes both scalar and vectored scrub ioctls.

Major responsibilities:
- Defines `meta_scrub_ops[]`, the dispatch table for every `XFS_SCRUB_TYPE_*`.
- Implements `xfs_scrub_metadata`, the core setup/scrub/repair/teardown state machine.
- Implements `xfs_ioc_scrub_metadata`, the single-operation ioctl path.
- Implements `xfs_ioc_scrubv_metadata`, the vectored ioctl path with barriers, optional rest periods, and scrub-by-handle support.
- Handles subordinate scrub contexts for repair code that needs to run a nested scrub type.

Important entry points:
- `xchk_probe`: probe scrub/repair availability.
- `xchk_scrub_create_subord` / `xchk_scrub_free_subord`: clone a scrub context with a different metadata type while preserving parent state.
- `xchk_teardown`: releases AG/rtgroup cursors, transactions, inode locks, xfiles, xmbuf targets, tempfiles, orphanage references, and fsgates.
- `xchk_validate_inputs`: validates scrub metadata fields based on operation type.
- `xfs_scrub_metadata`: full single metadata scrub/repair execution engine.
- `xfs_ioc_scrub_metadata`: user copy wrapper for one scrub.
- `xfs_ioc_scrubv_metadata`: user copy wrapper for scrub vectors.
- `xfs_scrubv_check_barrier`: cancels later vectored work if earlier operations failed according to a barrier mask.

Dispatch model:
- `ST_NONE`: probe-like calls with no object selector.
- `ST_FS`: whole-filesystem metadata.
- `ST_PERAG`: per-allocation-group metadata.
- `ST_INODE`: inode-scoped metadata.
- `ST_GENERIC`: scrubber-specific selector validation.
- `ST_RTGROUP`: realtime group metadata, with compatibility behavior for pre-rtgroups filesystems.

The dispatch table covers superblock, AG headers, AG btrees, inode record/forks, directory, xattr, symlink, parent pointers, realtime bitmap/summary/group btrees, quota types, filesystem counters, quotacheck, nlinks, health, dirtree, metapath, and rtgroup superblock.

Core scrub flow:
1. Trace start.
2. Reject shutdown and norecovery mounts.
3. Validate user inputs and filesystem feature support.
4. Allocate `struct xfs_scrub`.
5. Acquire freeze protection for repair operations.
6. Run the type-specific setup callback.
7. Run scrub or repair-evaluation callback.
8. Convert `-EDEADLOCK` into `XCHK_TRY_HARDER` retry and `-ECHRNG` into defer-op drain retry.
9. Update health if scrub completes.
10. If repair was requested and needed, call `xrep_attempt`; `-EAGAIN` loops back to setup/scrub.
11. Run postmortem logging if corruption remains.
12. Teardown and merge stats unless operation was not found.
13. Convert verifier corruption errnos into output flags with success errno.

Vectored scrub:
- Requires `CAP_SYS_ADMIN`, validates vector head and vector entries, copies at most one page of vector data from userspace, and traces every item.
- Supports `XFS_SCRUB_TYPE_BARRIER`, where `sv_flags` names output flags that should cancel later vector items if earlier work reported them.
- Can pin a scrub-by-handle inode across the vector run to avoid repeated untrusted lookups.
- Writes per-vector return code and output flags back to userspace.

Risk notes:
- Retry behavior is stateful: teardown must succeed before retry flags are applied.
- `xchk_teardown` commits a transaction only for successful repair requests; otherwise it cancels.
- Repair validation deliberately defers checking `ops->repair` until scrub proves repair is needed.
- Vectored scrub must keep ABI validation strict because vectors are copied from user memory and later copied back.
