# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/partitionview.py

Tree view listing OCFS2 partitions and coordinating selected-device UI state.

Key class:
- `PartitionView(gtk.TreeView)`
  - Model columns:
    - device
    - mountpoint
  - Selection change:
    - Enables selection-dependent widgets.
    - Enables mount widgets for mounted rows.
    - Enables unmount/action widgets for unmounted rows.
    - Rebuilds info frames for selected device.
  - `refresh_partitions()`
    - Disables action widgets.
    - Reads optional filter entry.
    - Rebuilds model.
    - Calls `partition_list(..., fstype='ocfs2', async=True)`.
    - Preserves previous device selection where possible.
  - `add_partition`
    - Callback from `plist.partition_list`.
  - Widget-list helpers:
    - `add_sel_widgets`
    - `add_mount_widgets`
    - `add_unmount_widgets`

Dependencies:
- `plist.partition_list`
- PyGTK

Notable details:
- Mounted devices sort before unmounted devices.
- Info tabs are recreated by destroying previous frame child and instantiating the info class with the selected device.
