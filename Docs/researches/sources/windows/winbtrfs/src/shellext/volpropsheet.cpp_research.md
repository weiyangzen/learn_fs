# File Research: sources/windows/winbtrfs/src/shellext/volpropsheet.cpp

## Purpose
Implements the Btrfs volume property sheet for Explorer. It exposes volume UUID, usage reporting, balance, devices, scrub, device stats reset, device add/remove/resize launchers, and drive-letter changes.

## Main Components
- COM integration:
  - `BtrfsVolPropSheet::QueryInterface`
  - `Initialize`: accepts a single Explorer-selected path, opens it, verifies WinBtrfs by querying devices, queries UUID, and creates `BtrfsBalance`.
  - `AddPages`: registers `IDD_VOL_PROP_SHEET` as a property page.
  - `ReplacePage`: no-op success.
- Usage reporting:
  - `FormatUsage`: converts `btrfs_usage` and `btrfs_device` buffers into text similar to Linux `btrfs fi usage`, including device totals, allocated/unallocated space, data/metadata ratios, profile sections, and per-device allocations.
  - `RefreshUsage`, `UsageDlgProc`, `ShowUsage`.
- Device management display:
  - `RefreshDevList`: queries devices and usage, populates a list view with ID, description, readonly, size, allocated, and allocation percent.
  - `DeviceDlgProc`: handles refresh, add/remove/resize launchers, stats dialog, and selection-sensitive button state.
  - `ShowDevices`.
- Device stats:
  - `StatsDlgProc`: displays per-device write/read/flush/corruption/generation stats.
  - `ResetStats`: launches elevated `rundll32` `ResetStats` action and refreshes device data.
  - Exported `ResetStatsW`: parses `volume|devid`, enables privilege, and sends `FSCTL_BTRFS_RESET_STATS`.
- Privileged action launchers:
  - `ShowScrub`: runs elevated `ShowScrub`.
  - `ShowChangeDriveLetter`: runs elevated `ShowChangeDriveLetter`.
  - Device add/remove/resize are also launched through elevated `rundll32.exe` commands.
- Main property dialog:
  - `PropSheetDlgProc`: initializes UUID display, readonly state, shield icons, and routes button clicks to usage/balance/devices/scrub/drive-letter actions.
- Drive-letter change:
  - `BtrfsChangeDriveLetter`: lists unused drive letters with mount manager queries, deletes the old DOS device symlink, creates the new one, and attempts rollback on failure.
  - Exported `ShowChangeDriveLetterW`.

## Data Flow
1. Explorer passes the selected item through `IDataObject`/`CF_HDROP`.
2. The selected path is opened with backup/reparse flags.
3. WinBtrfs driver FSCTLs provide devices, UUID, and usage.
4. Dialog actions either open local modal dialogs or spawn elevated `rundll32.exe shellbtrfs.dll,<Action> ...` helpers.
5. Device mutations and stats reset are followed by device list refreshes.

## Important Dependencies
- `shellext.h`: Win32/NT helpers, errors, RAII handles.
- `volpropsheet.h`: class declarations.
- `balance.h`, `scrub.h`: related volume operations.
- `mountmgr.h`: drive-letter mount point manipulation.
- `resource.h`: dialog/control/string IDs.
- WinBtrfs FSCTLs: `GET_DEVICES`, `GET_UUID`, `GET_USAGE`, `RESET_STATS`.

## Notable Behaviors and Edge Cases
- Device/usage buffers grow in 1024-byte increments up to eight retries on `STATUS_BUFFER_OVERFLOW`.
- `devices` is reused as class state; several refresh paths replace it and free old data.
- `FormatUsage` assumes metadata allocation totals are nonzero when computing metadata ratio.
- Device IDs are displayed as strings and later parsed with `_wtoi`, which truncates to integer width and may be fragile for very large `uint64_t` device IDs.
- Elevated commands concatenate paths and IDs into `rundll32` parameters; paths containing command separators used internally, especially `|`, could be problematic.
- Drive-letter change only supports root drive paths of the form `X:\`.
