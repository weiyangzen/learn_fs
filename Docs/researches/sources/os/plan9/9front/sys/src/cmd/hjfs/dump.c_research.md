# File Research: sources/os/plan9/9front/sys/src/cmd/hjfs/dump.c

Implements snapshot/dump support and copy-on-write preparation for `hjfs`.

Key points:
- `copydentry()` copies a dentry into a destination directory under a new name, increments references for direct and indirect blocks, and writes the destination dentry.
- `fsdump()` creates a date-based snapshot under the dump tree:
  - ensures a year directory exists
  - selects a unique month/day name
  - copies the root dentry into the dump directory
  - resets `LDUMPED` flags
- `resetldumped()` clears dump flags over the location tree.
- `willmodify1()` ensures a `Loc` is private before modification:
  - checks block refcount
  - if shared, finds parent block reference
  - asks `getblk(..., GBWRITE)` to allocate/copy as needed
  - updates descendant `Loc` records when the block changes
  - marks location dumped
- `willmodify()` walks the ancestor chain, upgrades locks when necessary, calls `willmodify1()` from rootward to leafward order, and retries if refcounts changed.

Dependencies and interactions:
- Uses channel, dentry, buffer, block reference, and allocation functions from the rest of `hjfs`.
- Called before mutating shared dumped data to preserve snapshots.

Research relevance:
- The snapshot/copy-on-write layer for `hjfs`, tying dump creation to refcounted block mutation.
