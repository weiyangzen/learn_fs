# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass1b.c

## Scope

Phase 1b for `fsck_ffs`: rescans allocated inodes to identify all inode references to blocks already marked duplicate in phase 1.

## Main APIs

- `pass1b()` initializes an address descriptor with `pass1bcheck()` and walks all inodes in all cylinder groups.
- `pass1bcheck()` compares each fragment in an inode block extent against the duplicate list.

## Control Flow

`pass1b()` starts `duphead` at `duplist` and rescans every non-`USTATE` inode at or above `ROOTINO` using `ckinode()`. For each block fragment, `pass1bcheck()` checks range validity and walks duplicate entries until `muldup`. On a match it reports `DUP`, moves the current duplicate to the head position, and advances `duphead`. The pass stops once all known duplicates have been found.

## Dependencies

- Uses `duplist`/`muldup` populated by `pass1check()`.
- Uses `ginode()`, `ckinode()`, `GET_ISTATE()`, `chkrange()`, and `blkerror()` from shared fsck code.

## Risks And Edge Cases

- Only runs in interactive mode; `main.c` treats duplicates with `-p` as an internal fatal condition.
- The duplicate-list mutation is order-sensitive and uses `duphead` to avoid rescanning already resolved duplicate reports.
