# sources/test-tools/stress-ng/stress-dirdeep.c

Purpose: implements `dirdeep`, a recursive directory-depth and inode-consumption stressor. It creates a deep tree with short directory names, symlinks, hardlinks, and optional per-directory files, then repeatedly traverses/exercises it before deleting it.

Important APIs/types/functions: `stress_dirdeep_inodes()` parses absolute or percent inode limits. `stress_dirdeep_make()` recursively creates directories, top-level link target, symlinks, hardlinks, optional files with fallocate, and `linkat()` variants. `stress_dir_exercise()` traverses with `scandir()`, touches file atimes with `open()`/`futimens()`, and occasionally fsyncs/syncfs. `stress_dir_tidy()` recursively removes files and directories in reverse sorted order. `stress_dirdeep()` ties options and lifecycle together.

Control flow: options determine bytes, subdirectories per level, files per level, and inode limit. The stressor records initial free inodes, builds a root temp path and link target, synchronizes start, recursively creates until path length, stop flag, filesystem limits, or inode budget halts creation, then loops traversing the tree until stop. Deinit recursively removes everything and reports exercised inode count.

State and persistence behavior: all created data is under the stress-ng temp path. Inode state is inferred from `stress_fs_available_inodes_get()` when available, with a local estimate fallback. `static bool tidy_info` suppresses repeated cleanup progress messages across invocations in the process.

Dependencies and integration points: depends on stress-ng temp path helpers, inode/free-space helpers, setting callbacks, sync/fallocate shims, and optional `linkat`, `unlinkat`, `futimens`, and `syncfs`. Registered with `dirdeep-bytes`, `dirdeep-dirs`, `dirdeep-inodes`, and `dirdeep-files`.

Risks: high branch factors and file counts can consume many inodes and path space quickly. The recursion relies on single-character directory names to preserve path headroom, but still stops on path length. Hardlink/symlink/linkat behavior varies across filesystems and permissions; expected capacity/permission errors stop creation without marking failure.

Test signals: run with low inode/file settings and with percent inode limits; verify cleanup removes the root tree, debug output reports inode use, and larger settings stop gracefully on ENOSPC/EDQUOT/EMLINK/ENAMETOOLONG.
