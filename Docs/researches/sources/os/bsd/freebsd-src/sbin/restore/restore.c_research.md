# File Research: sources/os/bsd/freebsd-src/sbin/restore/restore.c

Purpose: implements the core restore algorithms for listing, extraction selection, incremental reconciliation, file creation, link creation, and verification.

Key functions:
- `listfile()`, `addfile()`, and `deletefile()` are traversal callbacks used by list, extract, and interactive modes.
- `removeoldleaves()`, `nodeupdates()`, `findunreflinks()`, and `removeoldnodes()` implement incremental restore reconciliation against a previous filesystem symbol table.
- `createleaves()` extracts new or changed file contents for full/incremental restore and checkpoints after volume changes.
- `createfiles()` efficiently extracts only requested files for `-x` and `-i`, including volume skipping logic.
- `createlinks()` recreates whiteouts, hard links, and symbolic links for directory hard-link cases.
- `checkrestore()` and `verifyfile()` enforce that requested operations completed and no temporary names or flags remain.

Integration: heavily depends on symbol-table operations, tape position state, inode maps, directory traversal, and filesystem utility functions. `nodeupdates()` is the main state machine that classifies files by whether names/inodes are on tape, already known, or type-changed.

Risk notes: incremental reconciliation is complex and stateful. Directory deletion is deferred through `removelist`, and comments note `removeoldnodes()` can be slow for deep deletion sets. Incorrect flag combinations call `badentry()`/`panic()`.
