# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_traverse.c

This file implements generic ZFS block tree traversal over datasets, destroyed dataset root blocks, and whole pools. It is used by send, scrub-like walkers, estimates, and other DMU consumers that need ordered visits to block pointers and dnodes.

Core responsibilities:
- Defines traversal state `traverse_data_t` and prefetch state `prefetch_data_t`.
- Traverses ZIL blocks/records for non-snapshot datasets when appropriate, visiting claimed but unreplayed log blocks and stable read-only log blocks.
- Implements resume-aware traversal using `zbookmark_phys_t`, with skip modes for already completed subtrees and post-order resume semantics.
- Performs metadata prefetch for indirect, dnode, objset, and spill metadata when `TRAVERSE_PREFETCH_METADATA` is enabled.
- Supports data prefetch through a background traversal thread when `TRAVERSE_PREFETCH_DATA` is enabled, throttled by `zfs_pd_bytes_max`.
- Visits block pointers in `traverse_visitbp()`:
  - Skips blocks born before or at `td_min_txg`, with special handling for holes without birth times.
  - Calls callbacks in pre-order or post-order depending on flags.
  - Reads indirect blocks and recursively visits children.
  - Reads dnode blocks and recursively traverses contained dnodes.
  - Reads objset blocks and traverses meta/user/group/project-used dnodes.
  - Handles `TRAVERSE_HARD` by ignoring `EIO`/`ECKSUM`.
  - Records resume bookmark when traversal stops on error.
- Traverses individual dnodes in `traverse_dnode()`, including normal blkptrs and spill blkptrs.
- Implements public traversal entry points:
  - `traverse_dataset_resume()`
  - `traverse_dataset()`
  - `traverse_dataset_destroyed()`
  - `traverse_pool()`

Important control-flow notes:
- `traverse_impl()` is the central setup/teardown function. It initializes traversal state, handles hole-birth feature TXG, optionally traverses ZIL, launches prefetch traversal, performs the main root traversal, cancels prefetch, and destroys synchronization primitives.
- Root traversal starts at bookmark `(objset, ZB_ROOT_OBJECT, ZB_ROOT_LEVEL, ZB_ROOT_BLKID)`.
- Resume logic intentionally resumes at level-0 bookmarks even if traversal stopped at an indirect block.
- Hole birth behavior depends on `SPA_FEATURE_HOLE_BIRTH`, `send_holes_without_birth_time`, and whether object ID reallocation is possible.
- Protected/encrypted blocks are read with `ZIO_FLAG_RAW` when `TRAVERSE_NO_DECRYPT` is set.
- `traverse_pool()` walks the MOS first, then scans MOS objects for DSL dataset bonus types and traverses each dataset after its previous snapshot TXG.

Key dependencies:
- ARC reads/prefetch for block contents.
- Dnode and objset physical formats for recursive descent.
- DSL dataset/pool APIs for pool-wide traversal.
- ZIL parser for intent-log traversal.
- SPA feature state for hole birth behavior and raw/protected block handling.

Risk-sensitive invariants:
- Dataset contents must not be changing on disk during traversal, except for documented syncing/read-only contexts.
- Pre and post traversal flags are mutually exclusive.
- Prefetch resume state is separated from main resume state so prefetch can track progress without mutating caller state.
- Whole-pool traversal assumes a stable pool, such as zdb or sync context.
