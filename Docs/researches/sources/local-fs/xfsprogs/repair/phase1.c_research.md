# File Research: sources/local-fs/xfsprogs/repair/phase1.c

## Role

`phase1.c` implements xfs_repair phase 1: find, verify, and possibly repair the primary superblock.

## Main Flow

`phase1`:

- Logs phase start.
- Resets global repair-needed flags for root, metadir, realtime metadata, and quotas.
- Reads the primary superblock into an aligned AG buffer.
- If the primary superblock is unreadable or invalid, searches for a valid secondary superblock.
- Verifies and sets primary superblock geometry.
- Repairs `features2` versus `bad_features2` mismatch.
- Applies lazy counter conversion requests.
- Clears nonzero `shared_vn`.
- Writes the modified primary superblock unless in no-modify mode.
- Resets accumulated superblock counters.

## Helpers

- `alloc_ag_buf`: aligned AG header buffer allocation.
- `no_sb`: fatal path when no valid secondary superblock can be found.

## Repair Model

Phase 1 only repairs the superblock enough to let later phases mount libxfs geometry and scan the filesystem. Feature conversions are applied after superblock verification so subsequent phases operate against the intended feature set.
