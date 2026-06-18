# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/general.py

Displays general OCFS2 filesystem metadata for a selected device.

Key classes:
- `Field`
  - Base class with `fs`, `super`, `dinode`.
  - Returns `N/A` when no superblock is available.
  - Uses `class_label` for labels.
- Field subclasses:
  - `Version`
  - `Label`
  - `UUID`
  - `MaximumNodes`
  - `ClusterSize`
  - `BlockSize`
  - `FreeSpace`
  - `TotalSpace`
- `General(gtk.Table)`
  - Opens `ocfs2.Filesystem(device)`.
  - Reads `fs.fs_super`.
  - Looks up `GLOBAL_BITMAP_SYSTEM_INODE` and reads its cached inode.
  - Renders field labels and values in a table.

Dependencies:
- `ocfs2` C extension
- `classlabel.class_label`
- `guiutil.format_bytes`

Notable details:
- Free/total space are computed from bitmap inode fields and cluster/block sizing.
- OCFS2 open errors are silently converted into `N/A` display.
