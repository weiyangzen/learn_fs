# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rtsummary_repair.c

Implements online repair for the XFS realtime summary metadata file.

Key behavior:
- `xrep_setup_rtsummary` creates a hidden regular tempfile and reserves enough blocks for a complete replacement rtsummary plus worst-case bmbt overhead for preallocation and extent exchange.
- `xrep_rtsummary_prep_buf` copies generated summary words from the in-memory summary buffer into each tempfile block and installs either rtgroup-aware rtsummary headers/ops or legacy rt buffer ops.
- `xrep_rtsummary` requires `rmapbt` and atomic exchange-range support, repairs metadata inode forks first, preallocates the tempfile, copies rebuilt summary blocks, sets tempfile size, atomically exchanges contents, resets in-core rtsummary cache/state, and reaps the old fork blocks from the tempfile.

Important constraints:
- Repair aborts with `-EOPNOTSUPP` without reverse mappings or exchange-range support.
- If the scrubbed realtime bitmap block count disagrees with the superblock, repair returns success without changing anything.
- Tempfile locking is polled with termination checks because the rtsummary inode lock is already held.
