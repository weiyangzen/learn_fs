# File Research: sources/windows/winbtrfs/src/shellext/balance.cpp

## Purpose

`balance.cpp` implements the WinBtrfs shell extension UI and elevated command callbacks for Btrfs balance operations. It lets users configure balance filters, start balance, pause/resume balance, stop balance, and monitor progress through WinBtrfs FSCTLs.

## Balance Operation Launching

`BtrfsBalance::StartBalance()`:

- Builds a `btrfs_start_balance` structure from data, metadata, and system option sets.
- Enables or disables each option group based on dialog checkboxes.
- Serializes the binary request into a hex string.
- Relaunches the shell extension DLL through `rundll32.exe` using `ShellExecuteExW` with `lpVerb = "runas"` for elevation.
- Calls the exported `StartBalanceW` callback in the elevated process.
- Updates dialog state to running: disables main checkboxes/start, enables pause/cancel/progress.

`PauseBalance()` and `StopBalance()` use the same elevated `rundll32.exe` pattern, targeting `PauseBalanceW` and `StopBalanceW`.

Binary serialization helpers:

- `hex_digit()` and `serialize()` turn request bytes into wide-character hex.
- `from_hex_digit()` and `unserialize()` decode the elevated command-line payload back into `btrfs_start_balance`.

## Status Refresh

`BtrfsBalance::RefreshBalanceDlg()` opens the target path with backup/reparse flags and calls `FSCTL_BTRFS_QUERY_BALANCE`.

It updates UI based on status:

- Stopped:
  - disables pause/cancel/progress
  - enables option selection when not readonly
  - displays no balance, cancelled, complete, or failed messages
  - handles special text for remove-device and shrink-device flows
- Running or paused:
  - disables option selection
  - syncs checked data/metadata/system boxes from queried options
  - updates progress range and position from `total_chunks` and `chunks_left`
  - changes progress state for paused vs running
  - displays standard, removal, or shrinking progress text

The class tracks `cancelling`, `removing`, `shrinking`, and previous `balance_status` to avoid redundant UI resets and choose the correct localized messages.

## Option Saving

`BtrfsBalance::SaveBalanceOpts()` writes UI selections into one of:

- `data_opts`
- `metadata_opts`
- `system_opts`

Supported balance filters/options include:

- profiles: single, dup, RAID0, RAID1, RAID10, RAID5, RAID6, RAID1C3, RAID1C4
- device id
- physical/device range
- virtual range
- limit range
- stripe count range
- usage range
- conversion target
- soft conversion flag

The function validates start/end ordering for range-like filters and throws localized string errors if an end value is below its start value.

## Options Dialog

`BtrfsBalance::BalanceOptsDlgProc()` owns the balance options dialog.

On `WM_INITDIALOG` it:

- Selects the correct option set based on `opts_type`.
- Uses queried live options instead of stored options if balance is already running.
- Populates the device combo from the `btrfs_device` list.
- Populates the conversion combo from profile types, restricting RAID levels based on the number of writable devices.
- Initializes all checkboxes, spinners, edit fields, and enabled/disabled states.
- Disables editing while a balance is already running or paused.

On checkbox clicks it enables or disables dependent controls for each option category. On OK it either closes immediately for a running balance or calls `SaveBalanceOpts()` for an editable configuration.

`stub_BalanceOptsDlgProc()` stores and retrieves the `BtrfsBalance*` pointer through `GWLP_USERDATA` and forwards messages to the instance method.

## Main Balance Dialog

`BtrfsBalance::BalanceDlgProc()` owns the main balance dialog.

On initialization it:

- Clears option structures.
- Initializes remove/shrink status flags from constructor inputs.
- Calls `RefreshBalanceDlg(..., true)`.
- Applies readonly disabling.
- Adds UAC shield icons to start/pause/cancel buttons.
- Starts a one-second timer for status refresh.

Command handling covers:

- OK/cancel closing
- data/metadata/system checkbox changes
- option dialog buttons
- start, pause/resume, and cancel buttons

`stub_BalanceDlgProc()` is the instance forwarding thunk for the dialog procedure.

## Device Discovery

`BtrfsBalance::ShowBalance()`:

- Frees any old device list.
- Opens the target path.
- Calls `FSCTL_BTRFS_GET_DEVICES`, growing the buffer on `STATUS_BUFFER_OVERFLOW` up to a bounded retry count.
- Determines whether all devices are readonly.
- Shows the balance dialog with the populated state.

The device list is later used for device filters and conversion availability.

## Elevated Callback Exports

The file exports three `extern "C"` `CALLBACK` functions intended for `rundll32.exe`:

- `StartBalanceW`
  - Parses `<volume> <hex-request>` from the command line.
  - Enables `SeManageVolumePrivilege`.
  - Opens the volume/path.
  - Calls `FSCTL_BTRFS_START_BALANCE`.
  - If start returns `STATUS_DEVICE_NOT_READY`, queries scrub status and reports a scrub-running message when applicable.
- `PauseBalanceW`
  - Enables `SeManageVolumePrivilege`.
  - Opens the volume/path.
  - Queries balance status.
  - Calls `FSCTL_BTRFS_RESUME_BALANCE` if paused, or `FSCTL_BTRFS_PAUSE_BALANCE` if running.
- `StopBalanceW`
  - Enables `SeManageVolumePrivilege`.
  - Opens the volume/path.
  - Queries balance status.
  - Calls `FSCTL_BTRFS_STOP_BALANCE` if running or paused.

All callbacks catch exceptions and display shell-extension error messages.

## Integration

This file integrates the shell extension resource IDs, localized string loading, Win32 dialog APIs, elevation via ShellExecute/rundll32, `NtFsControlFile`, and WinBtrfs private IOCTL structures from `btrfsioctl.h`.

## Notable Details

- The elevated command channel serializes raw request bytes as hex on the command line; no separate IPC channel is used.
- Options are intentionally non-editable once a balance is running; live queried options are shown instead.
- The conversion profile list is constrained by writable device count.
- `unserialize()` assumes hex-like input and does not reject invalid characters explicitly; command input is generated internally by `serialize()`.
- `StartBalance()` waits for the elevated process to exit, so the UI thread blocks during the privileged FSCTL dispatch, though the balance itself is a kernel operation.
