# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass2.c

## Scope

Phase 2 for `fsck_ffs`: validates root inode state, checks all directory contents, repairs `.` and `..`, removes invalid directory entries, decrements expected link counts, records parent relationships, builds child lists, and marks directories reachable from root.

## Main APIs

- `pass2()` handles root inode repair, sorts cached directories by first block, runs directory scans, verifies `..`, builds child lists, and calls `propagate(ROOTINO)`.
- `pass2check()` is the directory-entry callback.
- `blksort()` orders directory inode info by disk block for better locality.

## Control Flow

The root inode is required to be a directory. If unallocated, bad, or a file, `pass2()` offers allocation, reallocation, or type correction. It marks root `DFOUND`, sorts `inpsort`, validates each directory size, creates a synthetic inode descriptor from cached block pointers, and scans entries through `ckinode()`.

`pass2check()` enforces first entry `.` and second entry `..`, including type fields. It removes extra `.`/`..`, out-of-range inode references, unallocated entries, and entries pointing to bad/duplicate inodes when approved. Directory hard links are diagnosed as extraneous and can be removed. Valid references decrement `ILNCOUNT()`, and directory entries update parent discovery.

A second pass fixes wrong or missing `..` after all parents are known. Finally children are linked under parents and reachability is propagated from root.

## Dependencies

- Directory and inode helpers: `ckinode()`, `makeentry()`, `changeino()`, `allocdir()`, `freeino()`, `getinoinfo()`, `getpathname()`, `propagate()`.
- Uses inode states `USTATE`, `DSTATE`, `DFOUND`, `DCLEAR`, `FSTATE`, `FCLEAR`.

## Risks And Edge Cases

- If a missing `.` or `..` cannot fit in existing record space, the code reports inability rather than reshaping the directory.
- Preen mode removes some bad directory entries automatically but leaves harder cases for interactive repair.
- The parent/child model assumes one real parent per directory and treats additional hard links to directories as extraneous.
