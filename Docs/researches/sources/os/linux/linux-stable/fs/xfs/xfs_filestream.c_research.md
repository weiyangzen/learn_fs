# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_filestream.c

## Purpose

Implements XFS filestream allocation policy, which associates directories with allocation groups to keep related file data streams localized and reduce allocation contention/fragmentation.

## Main Responsibilities

- Stores directory-to-AG associations in an MRU cache.
- Frees filestream associations and drops perag stream counts.
- Picks a suitable AG for a filestream allocation:
  - scans from a preferred AG
  - prefers AGs not already associated with another stream
  - checks longest free extent and minimum free-space thresholds
  - avoids metadata-preferred AGs for userdata unless low-space handling applies
  - falls back to the AG with the most free blocks
- Finds a file's parent directory from dcache aliasing.
- Looks up an existing filestream association and validates that the AG can satisfy the allocation.
- Creates or replaces associations when needed.
- Selects the target AG for bmap allocation through `xfs_filestream_select_ag`.
- Deletes associations for an inode.
- Initializes and destroys the mount MRU cache.

## Important Invariants

- `pagf_fstrms` acts both as an association count and as a selection exclusion mechanism.
- Existing association lookup returns a referenced perag if allocation can proceed there.
- On low-space transactions, cached associations are used more readily to avoid expensive searching.
- Association creation failures do not fail the allocation if a referenced AG was selected.
- In inode32 mode, a rotor is used to spread initial AG choices.

## Dependencies

- Uses `xfs_mru_cache`.
- Uses per-AG free-space queries through `xfs_bmap_longest_free_extent`.
- Uses bmap adjacency heuristics to bias allocation near preferred blocks.
- Uses perag reference and active reference accounting.

## Research Notes

Filestreams are allocation policy rather than correctness machinery. The main tradeoff is keeping related files together while avoiding overusing the same AG when enough free space exists elsewhere.
