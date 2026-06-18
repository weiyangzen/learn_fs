# File Research: sources/virtualization/nbd/treefiles.c

## Purpose
Implements helper functions for treefile exports, where an export is represented as a directory tree of 4KiB block files instead of one large file.

## Main Entry Points
- `construct_path()` recursively builds a path using `TREE%04X` directories and `FILE%04X` leaf files for a logical export position.
- `delete_treefile()` constructs and unlinks the block file for a logical offset.
- `mkdir_path()` creates all intermediate path components.
- `open_treefile()` opens or creates the block file for a logical offset under a mutex.

## Control Flow
`construct_path()` divides the export size by `TREEDIRSIZE` until it reaches leaf-file scale, encoding each path level from the logical page position. `open_treefile()` constructs the path, locks around open/create, creates missing directories when opening read-write, or creates an unlinked dummy tempfile for readonly missing blocks. Newly created block files are extended to `TREEPAGESIZE`.

## Dependencies
Uses POSIX file/path APIs, pthread mutexes, `PATH_MAX`, local `cliserv.h`, `treefiles.h`, and `nbd-debug.h`.

## Risks and Notes
The path builder mutates buffers recursively and relies on caller-provided size checks. Readonly missing blocks are served from a temporary zero-filled file, not from the tree. `mkdir_path()` mutates the path string in place while creating components.
