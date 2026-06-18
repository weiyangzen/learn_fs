# File Research: sources/local-fs/reiserfsprogs/fsck/lost+found.c

Implements rebuild-tree pass 3a: linking unreachable directories/files into `/lost+found`.

Main flow:
- `_look_for_lost(fs, link_lost_dirs)` scans tree items marked unreachable.
- First pass links lost directories.
- Second pass links lost regular files.
- `pass_3a_look_for_lost(fs)` updates `/lost+found` size, blocks, and mode, then flushes metadata.

Behavior:
- Skips already reachable items.
- Recovers missing directory stat data when a directory item exists without stat data.
- Avoids linking empty lost directories.
- Handles objectid sharing by relocating directories or rewriting files.
- Adds entries named `<dirid>_<objectid>` under `/lost+found`.
- Runs semantic rebuild on linked directories and regular-file validation on linked files.
- Marks recovered file stat data reachable.

State handling:
- `load_lost_found_result` initializes new/allocable bitmaps and objectid maps when resuming from a dump.
- `save_lost_found_result` writes a stage marker file.
- `after_lost_found` updates superblock fsck state, flushes objectid map/bitmap, prints stage report, and either exits or continues.

Notable details:
- Sets `/lost+found` mode to `drwx------`.
- Uses `semantic_id_map` to detect objectid reuse during recovery.
