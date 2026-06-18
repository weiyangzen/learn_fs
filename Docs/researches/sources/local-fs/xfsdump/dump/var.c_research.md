# File Research: sources/local-fs/xfsdump/dump/var.c

`var.c` manages xfsdump’s persistent state directory and prevents that directory from being included in dumps of the same filesystem.

Main functions:
- `var_create`: creates each component of `XFSDUMP_DIRPATH`, logging the path and stopping on first component-creation failure.
- `var_create_component`: calls `mkdir(path, 0755)` and, for newly created directories, attempts `chown(path, 0, 0)`.
- `var_skip`: obtains the filesystem UUID containing `XFSDUMP_DIRPATH` with `fs_getid`, compares it with the dump target UUID, and if they match recursively reports all inodes under the xfsdump state directory to a callback.
- `var_skip_recurse`: walks the directory tree with `lstat64`, `opendir`, `readdir`, and `open_pathalloc`, invoking the callback with each inode.

Integration:
- `content_init` calls `var_create()` before inventory work.
- After `inomap_build`, `content_init` calls `var_skip(&fsid, inomap_skip)` so xfsdump’s own inventory/state files are removed from the dump map.

Maintenance notes:
- Recursive traversal follows directory structure using `lstat64`; symlinks are reported but not descended.
- Errors opening/statting paths are logged and skipped rather than aborting the dump.
