# File Research: sources/local-fs/xfsprogs/repair/phase3.c

## Role

`phase3.c` implements phase 3: clear unlinked inode lists, verify uncertain inodes, process known inodes, and perform inode discovery through directories.

## AGI Unlinked Cleanup

`process_agi_unlinked` reads each AGI and clears all `agi_unlinked` buckets when modifying. This is delayed until phase 3 because inode clearing must not lose information before unlinked lists are examined.

## Known Inode Processing

`process_ag_func` waits for inode prefetch, then calls:

`process_aginodes(..., check_dirs=1, check_dups=0, extra_attr_check=1)`

This means phase 3 performs directory processing, inode discovery, and attribute semantic checks, but does not run duplicate-block checking.

`process_ags` runs this through the inode prefetch framework.

## Uncertain Inode Processing

`do_uncertain_aginodes` processes one AG’s uncertain inode records and returns how many new uncertain inodes were found.

`phase3` loops over all AGs until no uncertain inodes remain. This handles directory entries that point to inodes not present in the initial inode btrees.

## Phase Flow

`phase3`:

- Logs phase start and whether unlinked lists will be cleared.
- Checks realtime superblock metadata when applicable.
- Clears AGI unlinked lists if modifying.
- Checks uncertain inode records found before phase 3.
- Processes all known inodes with directory discovery enabled.
- Repeatedly processes newly discovered inodes in parallel until the uncertain sets are empty.

## Interactions

Phase 3 is where `dir2.c` and `dinode.c` cooperate most directly: directory entries can add uncertain inodes, and those inodes are then validated by `process_uncertain_aginodes`.
