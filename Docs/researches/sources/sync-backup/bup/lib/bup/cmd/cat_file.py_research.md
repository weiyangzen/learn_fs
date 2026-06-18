# sources/sync-backup/bup/lib/bup/cmd/cat_file.py

## Purpose
Implements `bup cat-file`, which prints file contents, encoded metadata, or raw `.bupm` metadata for a bup VFS path.

## Important APIs, Types, and Functions
Defines `optspec` and `main`. Uses `options`, `git.check_repo_or_die`, `LocalRepo`, `vfs.resolve`, `vfs.item_mode`, `vfs.tree_data_and_bupm`, `vfs.tree_data_reader`, `vfs.augment_item_meta`, `vfs.fopen`, and `chunkyreader`.

## Control Flow
Validates exactly one target and incompatible flags, requires `/branch/revision/...` shape, resolves without following symlinks, errors if missing, then branches: `--bupm` requires directory and streams `.bupm`; `--meta` writes encoded augmented metadata; default streams regular file data only.

## State and Persistence Behavior
Read-only repository access; writes selected bytes to stdout.

## Dependencies and Integration Points
Integrates command parsing, Git repo discovery, local repo abstraction, VFS resolution, metadata encoding, and byte-stream stdout.

## Risks and Test Signals
Risks include path validation excluding unusual but valid paths, symlink handling, non-regular file rejection, and missing `.bupm` silently writing nothing. Signals are exact stdout bytes and fatal errors for invalid targets/flag combinations.
