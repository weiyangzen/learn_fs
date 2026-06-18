# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota1_subr.c

Read completely: 90 lines.

Implements conversion helpers between legacy quota1 `struct dqblk` records and modern `struct quotaval` block/file values.

Functions:
- `dqblk2q2e_limit()` maps legacy limit zero to `UQUAD_MAX` for unlimited, otherwise maps stored `lim` to `lim - 1`.
- `q2e2dqblk_limit()` maps `UQUAD_MAX` back to zero, otherwise stores `lim + 1`.
- `lfs_dqblk_to_quotavals()` fills block and file `quotaval` structures from a `dqblk`, mapping hard/soft limits, current usage, and expire times.
- `lfs_quotavals_to_dqblk()` writes a `dqblk` from block and file `quotaval` structures.

Role:
- Normalizes legacy quota1's zero/unlimited and off-by-one limit representation to the filesystem-independent quota API.

Risks and notes:
- Comments question whether `qv_grace` is handled correctly; the functions only convert expire times and do not populate/store grace duration fields.
