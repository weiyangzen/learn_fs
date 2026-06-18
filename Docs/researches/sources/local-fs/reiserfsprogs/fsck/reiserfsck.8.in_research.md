# File Research: sources/local-fs/reiserfsprogs/fsck/reiserfsck.8.in

This file is the `reiserfsck(8)` manual page template.

Key content:
- Defines `reiserfsck` as the ReiserFS checking and repair tool.
- Documents main modes:
  - `--check`: default consistency check, no repair.
  - `--fix-fixable`: fixes limited corruption without full tree rebuild.
  - `--rebuild-tree`: rebuilds the full filesystem tree from discovered leaves.
  - `--rebuild-sb`: reconstructs a missing/damaged superblock.
  - `--clean-attributes`: clears old stat-data reserved fields before extended attributes use.
- Documents journal handling with `--journal` and expert `--no-journal-available`.
- Documents repair modifiers such as `--adjust-size`, `--badblocks`, `--logfile`, `--nolog`, `--quiet`, `--yes`, `--force`, and `--scan-whole-partition`.
- Gives an operational example: run `--check`, then `--fix-fixable` for exit code 1, or `--rebuild-tree` for fatal corruption/exit code 2.
- Lists exit codes 0, 1, 2, 4, 6, 8, and 16.
- Warns that `--rebuild-tree` should be backed up first and not interrupted once started.

Relationship to code:
- The documented pass behavior maps to the rebuild flow implemented by `pass0.c`, `pass1.c`, `pass2.c`, `semantic_rebuild.c`, and `pass4.c`.
- `--fix-fixable` behavior maps to semantic/stat-data fixes in `semantic_check.c` and shared file validation in `ufile.c`.
- `--rebuild-sb` maps to the interactive logic in `super.c`.

Notable documentation details:
- `--yes` is explicitly disabled for `--rebuild-tree` for safety.
- `--scan-whole-partition` expands rebuild-tree scanning beyond used blocks, matching pass-0 scan-area logic.
