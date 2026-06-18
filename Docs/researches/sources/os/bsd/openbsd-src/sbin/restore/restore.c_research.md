# File Research: sources/os/bsd/openbsd-src/sbin/restore/restore.c

## Purpose

Core restore algorithms: listing, marking extraction requests, deleting requests, computing incremental restore updates, removing obsolete names, extracting scheduled files, creating links, and validating symbol-table completion.

## Basic Listing And Marking

`listfile()` implements tape listing callbacks and prints entries present in `dumpmap`. `addfile()` marks dump entries for extraction, creating symbol table entries when needed and handling inode-name mode by generating literal directory files. `deletefile()` clears `NEW` on requested entries and frees non-directory entries.

## Incremental Restore State Machine

`removeoldleaves()` walks old symbol table entries and removes leaves whose inode is no longer in `usedinomap`; directories are given temp names, removed from inode lookup, and deferred on `removelist`.

`nodeupdates()` is the main incremental decision table. For each path from the new dump, it derives a key from whether the inode is on tape, inode exists, name exists, and file type changed. It then chooses KEEP, NEW, EXTRACT, LINK, rename, temp-name, remove, or deferred directory deletion behavior. It handles name/inode conflicts, hard links, mode/type changes, deleted hard links to directories, files created during dump, and inconsistent/impossible symbol-table states.

`findunreflinks()` removes unreferenced leaf names after node update processing, including leaves stranded inside removed directories. `removeoldnodes()` repeatedly removes empty deferred directories from `removelist`, reporting any non-empty remainder.

## Extraction Scheduling

`createleaves()` is used by full/incremental restore. It checkpoints before extraction, then walks tape file order against the lower bound of pending inodes, reports missing expected files, skips unexpected files, extracts files through `extractfile(myname(ep))`, clears `NEW|EXTRACT`, and checkpoints after volume changes.

`createfiles()` is used by extract/interactive modes. It rewinds to volume one, skips maps and directories, computes first/last requested inode bounds, skips volumes whose current inode is too high, skips forward to needed inodes, reports missed requested files, extracts matches, and clears `NEW`.

## Link And Verification Passes

`createlinks()` walks all entries and creates pending hard links or symlinks for directory hard-link cases. `checkrestore()` clears transient flags and reports incomplete operations. `verifyfile()` compares the final symbol table against the tape directory tree.

## Risks And Invariants

- Incremental correctness depends on the `nodeupdates()` key table; changing symbol-table flags or entry types can break rename/link semantics.
- Directories cannot be removed immediately when obsolete because live children may still need to be renamed out.
- Extraction assumes tape file order by inode and uses bounds from symbol table helpers (`lowerbnd()`, `upperbnd()`).
- Checkpointing after volume changes is required for `restore -R` resume.
