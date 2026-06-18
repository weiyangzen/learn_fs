# File Research: sources/local-fs/reiserfsprogs/fsck/super.c

`super.c` implements interactive superblock reconstruction and normalization for `reiserfsck --rebuild-sb`.

Key responsibilities:
- Determines filesystem version interactively when it cannot infer it from magic strings and superblock location.
- Handles both cases:
  - A ReiserFS superblock is found but contains damaged/inconsistent fields.
  - No usable ReiserFS superblock is found and a new one must be created.
- Normalizes or reconstructs:
  - ReiserFS format version
  - block count and block size
  - object-id map sizes
  - bitmap count
  - root block
  - free-block count
  - unmount state
  - object-id cursor size
  - tree height
  - hash code
  - UUID and superblock flags for newer formats
- Handles standard and non-standard journal layouts.
- Opens/checks the journal and compares journal-header parameters with superblock journal parameters.
- Prompts for journal offset and size when needed.
- Can mark journal as needing `reiserfstune` when `--no-journal-available` is used.
- Rebuilds the journal header after confirmation when parameters are inconsistent.
- Prints the candidate superblock and asks the user before writing it.

Important exported helper:
- `rebuild_sb()`

Dependencies and data flow:
- Uses ReiserFS creation/open/journal helpers, `count_blocks()`, journal-parameter advisory helpers, UUID support when available, and user confirmation routines.
- Mutates `fs->fs_ondisk_sb` and journal header buffers only after validation and user confirmation.

Notable behavior:
- This path is intentionally interactive and exits when complete.
- It sets `FS_ERROR` on rebuilt/modified superblocks so the filesystem still requires a subsequent `reiserfsck --check`.
- It refuses unsafe journal/superblock combinations, such as specifying a separate journal for a filesystem whose superblock indicates a default journal.
