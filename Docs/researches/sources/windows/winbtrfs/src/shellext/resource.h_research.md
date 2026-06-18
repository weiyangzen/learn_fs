# File Research: sources/windows/winbtrfs/src/shellext/resource.h

## Purpose
Central numeric resource ID registry for the WinBtrfs shell extension. It is generated-style Visual C++ resource metadata consumed by `shellbtrfs.rc.in` and C++ code.

## Main Contents
- Icon and dialog IDs:
  - `IDI_ICON1`
  - inode property dialogs: `IDD_PROP_SHEET`, `IDD_SIZE_DETAILS`
  - volume dialogs: `IDD_VOL_PROP_SHEET`, `IDD_VOL_USAGE`
  - balance/device/scrub dialogs: `IDD_BALANCE_OPTIONS`, `IDD_BALANCE`, `IDD_DEVICES`, `IDD_DEVICE_ADD`, `IDD_SCRUB`, `IDD_DEVICE_STATS`
  - send/receive dialogs: `IDD_RECV_PROGRESS`, `IDD_SEND_SUBVOL`
  - resize/drive-letter/mapping dialogs: `IDD_RESIZE`, `IDD_DRIVE_LETTER`, `IDD_MAPPINGS`
- String IDs for:
  - subvolume creation/snapshot menu labels and help.
  - inode type and size formatting.
  - volume usage and RAID/profile labels.
  - balance, scrub, device, resize, and drive-letter messages.
  - receive/send stream status and error text.
  - registry, mount manager, reflink, and mapping errors.
- Control IDs:
  - inode property controls such as `IDC_UID`, `IDC_GID`, permission checkboxes, compression flags.
  - usage/balance/device/scrub controls.
  - receive progress controls `IDC_RECV_PROGRESS`, `IDC_RECV_MSG`.
  - send controls `IDC_STREAM_DEST`, `IDC_PARENT_SUBVOL`, `IDC_CLONE_LIST`.
  - drive-letter and mapping controls.

## Dependencies
Used directly by all shell extension `.cpp` files in this group through `MAKEINTRESOURCEW`, `load_string`, `GetDlgItem`, and message dispatch.

## Notable Behaviors
- Some numeric IDs are intentionally reused for different dialogs, which is normal for Win32 resources because controls are scoped by dialog template.
- The file is generated-style and should be edited carefully, preferably through the resource script or Visual Studio resource tooling when maintaining numeric consistency.
