# sources/test-tools/unionmount-testsuite/remount_union.py

Purpose: remounts the active union during tests, optionally rotating the current upper layer into lower layers for multi-layer/recycle scenarios.

Important APIs/types/functions: `remount_union(ctx, rotate_upper=False)`.

Control flow: only acts for overlayfs testing. It unmounts the union, drops caches, checks kernel taint, and either keeps the current lower/upper/work directories or, when `rotate_upper` and more layers are available, prepends the current upper layer to `lowerdir`, advances the context layer number, creates a new layer with `u`/`w`, optionally mounts a per-layer tmpfs, and writes a pure upper file. It mounts overlay again and records current device and layer metadata.

State and persistence: mutates mount state, creates new upper layer directories, may mount tmpfs layers, and updates context-recorded lower/upper paths.

Dependencies and integration: called from context `mkdir`, `rename`, and `link` paths when recycle/rotation checks are active. Depends on `tool_box.system`, `check_not_tainted`, and `write_file`.

Risks: assumes unmount/drop-caches privileges; layer rotation is string-concatenated lowerdir order; only overlayfs path is implemented; remount failures stop the suite.

Test signals: multi-layer runs such as `--ov=N` validate inode stability and copy-up behavior across remounts.
