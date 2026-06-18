# File Research: sources/local-fs/dosfstools/src/check.c

Core `fsck.fat` directory-tree and metadata repair engine.

Major responsibilities:
- Builds an in-memory tree of `DOS_FILE` entries from root and subdirectories.
- Tracks cluster ownership through `fat.c` owner table.
- Validates and repairs:
  - bad short names
  - duplicate directory entries
  - broken `.` and `..` entries
  - invalid start clusters
  - directories with nonzero size
  - self-referential or parent-referential directories
  - free/bad clusters inside file chains
  - circular cluster chains
  - cross-linked cluster chains
  - file-size versus cluster-chain length mismatches
  - requested drop/undelete operations
  - dirty flags
  - boot-sector and root-directory label mismatches.

Important helpers:
- `path_name()` builds display paths, preferring LFN names.
- `file_stat()` formats size/date metadata for duplicate-entry decisions.
- `bad_name()` validates 8.3 names, with Atari and `-S` no-middle-space modes.
- `drop_file()`, `truncate_file()`, `auto_rename()`, and `rename_file()` implement repair actions.
- `handle_dot()` validates or creates `.` and `..` entries.
- `check_file()` validates cluster chains, ownership, file sizes, and shared cluster handling.
- `check_dir()` checks bad names and duplicate names inside one directory.
- `test_file()` detects loops and optionally read-tests clusters.
- `undelete()` reconstructs a deleted file’s chain by linking contiguous free clusters.
- `add_file()` reads one directory slot, handles LFN state, applies drop/undelete rules, and adds a `DOS_FILE`.
- `scan_dir()`, `subdirs()`, and `scan_root()` perform recursive traversal.
- `check_dirty_bits()` clears FAT dirty/clean-shutdown state for FAT12/16/32.
- `check_label()` reconciles root-directory and boot-sector labels, validates label characters, and optionally enforces uppercase-only labels.

Key dependencies:
- `fat.c`: cluster chain traversal, ownership, FAT mutation.
- `io.c`: queued or immediate on-disk writes.
- `lfn.c`: long filename sequence parsing and repair.
- `file.c`: user-requested drop/undelete path descriptors and short-name formatting.
- `boot.c`: label and root-directory allocation helpers.
- `common.c`: interactive choices, memory queue, input, diagnostics.
- `charconv.c`: label validation and conversion.

Control-flow significance:
- `scan_root()` returns nonzero when repair invalidates traversal enough to require another pass.
- `fsck.fat.c` loops `read_fat(...), scan_root(...)` until scanning stabilizes.
- Cluster owner bookkeeping is first used transiently by `test_file()` and then permanently by `check_file()` for cross-link detection.

Research notes:
- This file is the highest-level FAT repair policy layer.
- Most repair choices are routed through `get_choice()`, so the same code supports interactive and automatic/noninteractive modes.
