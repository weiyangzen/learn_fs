# File Research: sources/windows/winbtrfs/src/shellext/contextmenu.cpp

Read status: complete, 1668 lines.

This file implements the WinBtrfs Explorer context-menu extension and the exported `ReflinkCopyW` rundll entry point. It exposes menu actions for creating subvolumes, creating snapshots, sending and receiving subvolumes through elevated helper UIs, and reflink-pasting clipboard file selections.

Key implementation points:
- `BtrfsContextMenu::Initialize` distinguishes selected-item context menus from directory-background menus. For selected files, it scans `CF_HDROP` paths and enables snapshot creation only for Btrfs subvolume roots, identified through `FSCTL_BTRFS_GET_FILE_IDS` with inode `0x100` and `top == false`.
- Directory-background initialization checks create-subdirectory permission and verifies the target is on Btrfs before enabling background commands.
- `QueryContextMenu` inserts localized menu entries. UAC-shield bitmaps are loaded through WIC and attached to elevated send/receive commands.
- `InvokeCommand` dispatches by verb or command id to snapshot creation, new subvolume creation, elevated send/receive GUI launches, or reflink paste.
- Snapshot and subvolume creation use WinBtrfs ioctls `FSCTL_BTRFS_CREATE_SNAPSHOT` and `FSCTL_BTRFS_CREATE_SUBVOL`, with collision-resistant default names.
- The reflink copy path checks source and destination are on the same volume before cloning.

The reflink implementation is the largest behavior in the file:
- `BtrfsContextMenu::reflink_copy` is used by Explorer clipboard paste and handles duplicate destination names.
- `reflink_copy2` is the command-line/rundll variant used by `ReflinkCopyW`.
- Subvolume roots are copied as Btrfs snapshots rather than cloned file trees.
- Special Btrfs inode types such as char/block devices, FIFO, and sockets are recreated via `FSCTL_BTRFS_MKNOD`.
- Regular files are cloned with `FSCTL_DUPLICATE_EXTENTS_TO_FILE` after matching EOF, sparse state, and integrity/checksum settings.
- Directories are recursively copied, excluding `.` and `..`.
- Reparse points are preserved with `FSCTL_GET_REPARSE_POINT` and `FSCTL_SET_REPARSE_POINT`.
- Alternate data streams and Btrfs xattrs are copied after file data/metadata.
- Inode flags and compression type are preserved through `FSCTL_BTRFS_SET_INODE_INFO`.
- On failure after destination creation, it attempts to delete the partial destination with `FileDispositionInformation`.

Important dependencies and integration:
- Uses shared helpers from `shellext.h` and `main.cpp`: `load_string`, `wstring_sprintf`, error classes, `command_line_to_args`, handle wrappers, and `module`.
- Uses WinBtrfs ioctl definitions from `../btrfsioctl.h`.
- Registered by `main.cpp` under `Directory\\Background` and `Folder` context-menu handlers.
- Instantiated by `Factory::CreateInstance` for `FactoryContextMenu`.

Risk and maintenance notes:
- Several paths use `MAX_PATH` buffers, so long-path behavior may be incomplete.
- `GetCommandString` rejects any `idCmd != 0` before later branches for id `1` and `2`, making help text/verbs for nonzero commands unreachable through that code path.
- The code relies on inode `0x100` for subvolume-root detection; an in-file FIXME notes this assumption.
- Many Btrfs control buffers are manually allocated and populated. Most are freed correctly, but this style is sensitive to early throws and length calculations.
- Alternate streams are cast to `uint16_t` size with a comment that Btrfs streams are expected below 64 KB; this assumption should stay documented if stream support changes.
