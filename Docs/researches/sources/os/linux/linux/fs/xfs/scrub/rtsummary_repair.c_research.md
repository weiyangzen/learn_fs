# File Research: sources/os/linux/linux/fs/xfs/scrub/rtsummary_repair.c

This file implements online repair for the XFS realtime summary metadata file. It stages a freshly generated realtime summary into a hidden temporary regular file, atomically exchanges the mappings with the real summary file, resets incore summary state, and reaps the old blocks.

Key entry points:
- `xrep_setup_rtsummary(struct xfs_scrub *sc, struct xchk_rtsummary *rts)`: creates the repair tempfile and adds a conservative block reservation for a complete summary rewrite plus bmbt overhead.
- `xrep_rtsummary(struct xfs_scrub *sc)`: main repair path for the realtime summary.
- `xrep_rtsummary_prep_buf(...)`: per-block copy-in callback used by `xrep_tempfile_copyin`.

Control flow:
1. Setup creates an `S_IFREG` tempfile and reserves `m_rsumblocks + 2 * xfs_bmbt_calc_size(...)`.
2. Repair requires `rmapbt` and exchange-range support.
3. It refuses to proceed if the checked bitmap block count disagrees with the superblock.
4. It repairs metadata inode forks first with `xrep_metadata_inode_forks`.
5. It try-locks the tempfile inode while already holding the realtime summary inode lock.
6. It joins both inodes to the transaction, preallocates summary file blocks, copies generated summary bytes from `xfsum_copyout`, and sets the tempfile size.
7. It reserves exchange resources, exchanges contents, invalidates/reset caches and mount summary geometry, then reaps the old fork blocks from the tempfile.

Important dependencies:
- `scrub/tempfile.h` and `scrub/tempexch.h` provide staging and atomic mapping exchange.
- `scrub/rtsummary.h` provides the generated summary data and `xfsum_copyout`.
- `scrub/reap.h` frees the old mapping set after exchange.
- `xfs_rtbitmap.h`, `xfs_rtalloc.h`, and realtime group state define summary formats and rtgroup behavior.

Data/format handling:
- For rtgroup-enabled filesystems, copied buffers receive `XFS_RTSUMMARY_MAGIC`, owner inode, block address, metadata UUID, and `xfs_rtsummary_buf_ops`.
- For older non-rtgroup realtime layouts, buffers use `xfs_rtbuf_ops`.
- Transaction buffer type is set to `XFS_BLFT_RTSUMMARY_BUF`.

Risk notes:
- Repair is intentionally unavailable without `rmapbt` and exchange-range support.
- Block reservation must be made before the replacement summary extent count is known, so it intentionally overestimates.
- The function cannot drop the realtime summary ILOCK once dirty transaction state exists, which explains the early reservation strategy.
