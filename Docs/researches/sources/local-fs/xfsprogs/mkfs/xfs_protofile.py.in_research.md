# File Research: sources/local-fs/xfsprogs/mkfs/xfs_protofile.py.in

## Purpose
Generates a mkfs.xfs protofile from one or more source directory trees.

## Key Elements
Emits the legacy protofile header `/` and `0 0`, then either emits a minimal empty root directory or walks supplied directories recursively. `stat_to_str` converts file type, suid/sgid bits, mode, uid, and gid into protofile format. `stat_to_extra` emits regular-file source path, device major/minor, or symlink target.

`walk_tree` separates files and directories, skips sockets, rejects names containing spaces, aligns file-name columns, emits files before directories, recursively descends subdirectories, and emits `$` directory terminators.

## Dependencies
Uses Python `os`, `argparse`, `sys`, `stat`, gettext substitution via `@INIT_GETTEXT@`, and build-time `@pkg_version@`.

## Behavior/Risks
Generated protofiles cannot represent filenames containing spaces because mkfs protofile parsing is whitespace-tokenized. Socket files are ignored. There is a likely error path bug: when the first supplied path is not a directory, `raise NotADirectoryError(path)` references `path` before the loop assigns it.
