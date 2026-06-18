# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/console.py

Main OCFS2 Console window.

Key class:
- `Console(gtk.Window)`
  - Creates main window titled `OCFS2 Console`.
  - Adds notebook tabs:
    - `General`
    - `File Listing`
  - Creates `PartitionView` and wires info frames to selected device.
  - Adds menu and toolbar.
  - Connects selection-sensitive menu/toolbar widgets.
  - Provides action methods for:
    - refresh
    - mount/unmount
    - format
    - relabel
    - slot count tuning
    - check/repair
    - node configuration
    - push cluster config
    - about

Dependencies:
- `PartitionView`
- `Menu`
- `Toolbar`
- `mount`, `format`, `fsck`, `tune`
- `General`, `Browser`
- `node_config`, `push_config`

Notable details:
- Delegates most action implementation to helper modules.
- Calls `process_gui_args()` before starting GUI.
- Refreshes partition list at startup.
