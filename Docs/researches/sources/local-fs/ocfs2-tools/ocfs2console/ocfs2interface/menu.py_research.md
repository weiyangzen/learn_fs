# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/menu.py

Builds the main OCFS2 Console menubar and selection-state widget lists.

Menu groups:
- File:
  - Quit
- Cluster:
  - Configure Nodes
  - Propagate Configuration, only if terminal/VTE support is available
- Tasks:
  - Format
  - Check, only if fsck terminal support is available
  - Repair, only if fsck terminal support is available
  - Change Label
  - Edit Node Slot Count
- Help:
  - About

Key constants:
- `UNMOUNTED_ONLY`
- `NEED_SELECTION`

Key class:
- `Menu`
  - Converts declarative `menu_data` into `gtk.ItemFactory` items.
  - Resolves callbacks through `guiutil.make_callback`.
  - Returns:
    - menubar widget
    - widgets needing a selection
    - widgets needing an unmounted partition

Dependencies:
- `fsck.fsck_ok`
- `pushconfig.pushconfig_ok`
- `guiutil.make_callback`

Notable details:
- Uses legacy `gtk.ItemFactory`.
- Action sensitivity is delegated to `PartitionView`, which receives the special widget lists.
