# File Research: sources/local-fs/ocfs2-tools/fswreck/include/extent.h

This header declares extent corruption helpers and the shared regular-file creation helper.

Exports:
- `mess_up_extent_list()`
- `mess_up_extent_block()`
- `mess_up_extent_record()`
- `create_file()`

Integration notes:
- `create_file()` is reused by inode, directory, symlink, and refcount corruption modules.
