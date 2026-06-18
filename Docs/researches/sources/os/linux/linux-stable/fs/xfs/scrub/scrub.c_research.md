# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/scrub.c

Provides the top-level online scrub and repair dispatcher for XFS.

Key behavior:
- Defines `meta_scrub_ops`, mapping every `XFS_SCRUB_TYPE_*` to its setup, scrub, optional repair, optional repair-evaluation, feature predicate, and input type.
- `xchk_validate_inputs` sanitizes userspace scrub requests, enforces per-type input rules, handles realtime group compatibility, rejects force-rebuild without repair, and limits repair to writable v5/crc filesystems.
- `xfs_scrub_metadata` runs the full operation lifecycle: shutdown/norecovery checks, setup, scrub, health update, optional repair, retry-on-`-EDEADLOCK`, retry-with-drain-on-`-ECHRNG`, teardown, stats merge, and final trace emission.
- `xchk_teardown` centralizes cleanup of AG/RT cursors, transactions, inode locks/references, freeze protection, xfiles, buffers, tempfiles, orphanage state, and enabled fs gates.
- `xfs_ioc_scrub_metadata` implements the single scrub ioctl with `CAP_SYS_ADMIN`, copy-in, dispatch, and copy-out.
- `xfs_ioc_scrubv_metadata` implements vectored scrub, including vector validation, optional scrub-by-handle inode pinning, barrier vectors, per-item results, optional rest delays, and signal interruption.

Important supporting logic:
- Probe scrub forces the corrupt flag when userspace probes repair on repair-capable kernels.
- Subordinate scrub contexts can temporarily switch scrub type while sharing selected parent resources.
- Postmortem logging differs depending on whether online repair is configured.
- Stats are collected only for non-`ENOENT` outcomes.
