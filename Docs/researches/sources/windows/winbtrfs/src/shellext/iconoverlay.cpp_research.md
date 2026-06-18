# File Research: sources/windows/winbtrfs/src/shellext/iconoverlay.cpp

Read status: complete, 80 lines.

This file implements the shell icon overlay handler for Btrfs subvolume roots.

Key behavior:
- `BtrfsIconOverlay::QueryInterface` supports `IUnknown` and `IShellIconOverlayIdentifier`.
- `GetOverlayInfo` returns the current module path as the icon source, icon index `0`, and flags for icon file and index.
- `GetPriority` returns priority `0`.
- `IsMemberOf` opens the path without following reparse points and calls `FSCTL_BTRFS_GET_FILE_IDS`.
- A path is considered an overlay member when it is a Btrfs subvolume root: inode `0x100` and `top == false`.

Integration:
- Registered by `main.cpp` under `ShellIconOverlayIdentifiers\\WinBtrfs`.
- Created by `Factory::CreateInstance` for `FactoryIconHandler`.
- Uses `../btrfsioctl.h` for file-id ioctl structures.

Risk and maintenance notes:
- Like context-menu snapshot detection, it assumes subvolume root inode `0x100`.
- Priority `0` competes with other overlay handlers. Windows also limits active overlay handlers, so registration order can affect visibility.
