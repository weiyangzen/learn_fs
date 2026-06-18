# File Research: sources/windows/winbtrfs/src/shellext/propsheet.cpp

Read status: complete, 1384 lines.

This file implements the WinBtrfs file/folder property sheet page and the exported standalone `ShowPropSheetW` dialog.

Main responsibilities:
- Adds a property page for Btrfs-selected files and folders.
- Reads Btrfs inode metadata using `FSCTL_BTRFS_GET_INODE_INFO`.
- Displays subvolume ID, inode ID, inode type, size-on-disk, compression ratio, fragmentation, inode flags, compression type, POSIX mode bits, uid, gid, and subvolume read-only state.
- Supports multi-selection by tracking min/max mode, flags, compression type, uid/gid, inode, type, and subvolume values.
- Walks selected directories asynchronously to update aggregate size/compression/fragmentation metrics.

Initialization and data loading:
- `Initialize` accepts only selected-item shell data, reads `CF_HDROP`, calls `load_file_list`, and starts a background search thread if directories need recursive accounting.
- `set_cmdline` provides equivalent initialization for elevated standalone use through `ShowPropSheetW`.
- `check_file` opens each file with `MAXIMUM_ALLOWED`, determines access rights, reads inode info, tracks whether admin relaunch is useful, and accumulates size/allocation/compression metadata.
- `do_search` recursively scans directories using `FindFirstFileW` and opens child files to accumulate Btrfs extent metrics.
- `search_list_thread` drains queued directories and sets `thread` to null when done.

Property editing:
- `change_inode_flag` edits Btrfs inode flags and enforces UI rules around `NODATACOW`, `NODATASUM`, and compression.
- `change_perm_flag`, `change_uid`, and `change_gid` track POSIX metadata edits.
- `apply_changes_file` reopens each target with required permissions and applies:
  - Btrfs inode flags,
  - POSIX mode,
  - uid and gid,
  - compression type,
  - subvolume read-only Windows attribute for subvolume roots.
- `apply_changes` applies pending edits to either the standalone filename or all shell-selected files.
- `open_as_admin` relaunches `ShowPropSheet` through elevated `rundll32.exe`, then reloads state.

UI behavior:
- `init_propsheet` populates controls, tri-state checkboxes for mixed selections, compression-type combo entries, permission bits, uid/gid fields, and optional admin button.
- `set_size_on_disk` formats total on-disk size, compression ratio, and fragmentation ratio. It is called periodically while the background thread is active.
- `SizeDetailsDlgProc` shows per-compression-class size details and refreshes while scanning is still active.
- `PropSheetDlgProc` handles control edits, apply notifications, size-detail links, and timer refreshes.
- `AddPages` creates the Explorer property sheet page and increments the COM object reference if accepted by Explorer.
- `ShowPropSheetW` creates a standalone one-page property sheet for elevated/admin editing.

Integration:
- Declared in `propsheet.h`.
- Created by `Factory::CreateInstance` for `FactoryPropSheet`.
- Registered by `main.cpp` under file and folder property sheet handlers.
- Uses shared helpers from `main.cpp` and Btrfs ioctl structures from `../btrfsioctl.h`.

Risk and maintenance notes:
- The background directory scan updates shared counters and `search_list` without visible synchronization while the UI thread reads them. This can race.
- Destructor does not wait for `thread`; lifetime safety depends on the property sheet staying alive until the scan ends.
- `change_inode_flag` and `change_perm_flag` set `flags_set = ~flag` or `mode_set = ~flag` for indeterminate state, which overwrites the whole mask rather than clearing one bit. This looks suspicious for mixed-selection editing.
- Several selected-file paths use `MAX_PATH`.
- Admin relaunch loops over selected files one at a time and blocks waiting for each elevated process.
