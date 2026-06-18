# File Research: sources/windows/winbtrfs/src/shellext/shellbtrfs.rc.in

## Purpose
CMake-templated Windows resource script for `shellbtrfs.dll`. It defines the shell extension icon, version metadata, dialog layouts, manifest, and English UK localized strings.

## Main Resource Areas
- Includes `resource.h` from the configured CMake source directory.
- Icon:
  - `IDI_ICON1` uses `subvol.ico`.
- Version block:
  - Uses `@PROJECT_VERSION_MAJOR@`, `@PROJECT_VERSION_MINOR@`, and `@PROJECT_VERSION_PATCH@`.
  - Identifies product as WinBtrfs and original filename as `shellbtrfs.dll`.
- Dialog templates:
  - `IDD_PROP_SHEET`: inode properties, POSIX permissions, flags, compression, subvolume readonly, admin open.
  - `IDD_SIZE_DETAILS`: inline/uncompressed/ZLIB/LZO/Zstd size details.
  - `IDD_VOL_PROP_SHEET`: volume UUID plus usage, balance, devices, scrub, and drive-letter actions.
  - `IDD_VOL_USAGE`: multiline usage report with refresh.
  - `IDD_BALANCE_OPTIONS`, `IDD_BALANCE`: balance filters/options/status controls.
  - `IDD_DEVICES`, `IDD_DEVICE_ADD`, `IDD_DEVICE_STATS`: device list, add tree, stats/reset.
  - `IDD_SCRUB`: scrub progress/status/info controls.
  - `IDD_RECV_PROGRESS`: receive progress dialog.
  - `IDD_SEND_SUBVOL`: send stream destination, incremental parent, clone list controls.
  - `IDD_RESIZE`: device resize slider/status.
  - `IDD_DRIVE_LETTER`: drive-letter combo dialog.
  - `IDD_MAPPINGS`: UID/GID mapping list tabs.
- Manifest:
  - Embeds `shellbtrfs.manifest`.
- String tables:
  - User-facing menu/help text.
  - Inode type and size strings.
  - Usage/profile/RAID labels.
  - Balance, device, scrub, send, receive, resize, mount manager, and mapping messages/errors.

## Important Dependencies
- `resource.h` numeric IDs must match the dialogs and strings defined here.
- C++ files call `load_string(module, IDS_...)` for these localized messages.
- Dialog procedures rely on the control IDs and layouts defined here.

## Notable Behaviors
- The file is source-templated rather than raw `.rc`; CMake substitutes paths and version fields.
- Dialogs use classic Win32 resource templates and fixed dialog units.
- This file is the localization source for many detailed error messages emitted by the send/receive/scrub/volume property code.
