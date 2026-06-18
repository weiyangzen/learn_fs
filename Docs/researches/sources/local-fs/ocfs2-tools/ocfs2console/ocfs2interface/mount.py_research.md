# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/mount.py

Mount and unmount workflows for OCFS2 devices.

Key functions:
- `mount(parent, device)`
  - Prompts for mountpoint/options using `query_mount`.
  - Runs `mount -t ocfs2 [-o options] device mountpoint` via `Process`.
  - Returns mountpoint on success.
  - Shows error dialogs on failure or killed process.
- `unmount(parent, device, mountpoint)`
  - Runs `umount mountpoint` via `Process`.
  - Shows error dialogs on failure or killed process.
- `query_mount(parent, device)`
  - Builds dialog with mountpoint and options entries.
  - Enables OK only for absolute mountpoint-like strings.
  - Prefills values from `get_defaults`.
- `get_defaults(device)`
  - Reads OCFS2 label/UUID.
  - Looks in `/etc/fstab` for matching device/LABEL/UUID and `vfstype == 'ocfs2'`.
- `get_ocfs2_id(device)`
  - Opens `ocfs2.Filesystem` and extracts superblock label/UUID.

Dependencies:
- `ocfs2` C extension
- `fstab.FSTab`
- `process.Process`

Notable details:
- Uses command tuple/list form for subprocess execution.
- Mountpoint validation is minimal: starts with `/` and length > 1.
