# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/iscan.h

This header defines the live inode scanner state and public API.

Key structure:
- `struct xchk_iscan`
  - scrub context
  - mutex-protected scan cursors
  - optional `skip_ino`
  - operation bits for aborted scans and AGI trylock mode
  - iget timeout/retry fields
  - batch base inode, skipped mask, and inode reference array

Operation bits:
- `XCHK_ISCAN_OPSTATE_ABORTED`
- `XCHK_ISCAN_OPSTATE_TRYLOCK_AGI`

Inline helpers:
- `xchk_iscan_aborted`
- `xchk_iscan_abort`
- `xchk_iscan_agi_needs_trylock`
- `xchk_iscan_set_agi_trylock`

Exported API:
- Start, finish early, teardown.
- Iterate and finish iteration.
- Mark an inode visited.
- Query whether a live update should be applied.

Integration:
- Used by parent finding, inode repair mode inference, and any scrub/repair code that builds metadata from a live full-inode scan.
