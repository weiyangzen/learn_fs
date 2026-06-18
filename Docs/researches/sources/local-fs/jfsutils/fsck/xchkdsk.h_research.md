# File Research: sources/local-fs/jfsutils/fsck/xchkdsk.h

## Purpose
Defines option-index constants used by `jfs_fsck` to record parsed command-line behavior in `agg_recptr->parm_options`.

## Key Elements
Contains include guards and a single `enum xchkdsk_options` with entries for check levels, if-dirty/autocheck behavior, verbosity/debug, clear-bad-block-list support, diagnostic block/inode/filename options, and the total `UFS_CHKDSK_OPTIONS` count.

The active users in this group are `xchkdsk.c` option parsing and verification routines, which set and inspect values such as `UFS_CHKDSK_LEVEL0`, `UFS_CHKDSK_LEVEL2`, `UFS_CHKDSK_LEVEL3`, `UFS_CHKDSK_IFDIRTY`, `UFS_CHKDSK_VERBOSE`, `UFS_CHKDSK_DEBUG`, `UFS_CHKDSK_CLRBDBLKLST`, and `UFS_CHKDSK_SKIPLOGREDO`.

## Dependencies
No external includes. The enum values are consumed by fsck aggregate-record option arrays declared in the internal fsck headers.

## Behavior/Risks
The enum order is part of the implicit ABI between option parsing and the aggregate record’s fixed-size option array. Adding or reordering entries would require checking all `parm_options[...]` indexing sites.
