# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/ls.py

Defines file metadata fields shown by the OCFS2 browser, similar to selected `ls -l` columns.

Key classes:
- `Field`
  - Base for rendering a dentry/dinode attribute as text.
- `Mode`
  - Builds file mode string from OCFS2 dentry type and inode mode bits.
- `Links`
  - Link count.
- `ID2Name`
  - Base for UID/GID to name resolution.
- `Owner`
  - Uses `pwd.getpwuid`.
- `Group`
  - Uses `grp.getgrgid`.
- `Size`
  - Inode size.
- `AllocSize`
  - `i_clusters * fs_clustersize`.
- `Timestamp`
  - Formats mtime using GNU-coreutils-style recent/old format decision.
- `Name`
  - Returns dentry name, though not included in exported `fields`.

Export:
- `fields = (Mode, Links, Owner, Group, Size, AllocSize, Timestamp)`

Dependencies:
- Python `stat`, `pwd`, `grp`, `time`
- `ocfs2` file type constants
- `class_label`

Notable details:
- `Mode` maps OCFS2 file types to single-character type indicators.
- Owner/group fall back to numeric IDs if system lookup fails.
