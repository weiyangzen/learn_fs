# File Research: sources/windows/winbtrfs/src/shellext/balance.h

## Purpose

`balance.h` declares the `BtrfsBalance` shell-extension class used to display and control WinBtrfs balance operations.

## Public Interface

- `BtrfsBalance(const wstring& drive, bool RemoveDevice = false, bool ShrinkDevice = false)`
  - Stores the target drive/path.
  - Records whether the dialog was opened from remove-device or shrink-device workflows.
  - Initializes `devices` to `nullptr` and `removing` to false.
- `void ShowBalance(HWND hwndDlg)`
  - Entry point that gathers device information and opens the main balance dialog.
- `INT_PTR CALLBACK BalanceDlgProc(...)`
  - Instance dialog procedure for the main balance dialog.
- `INT_PTR CALLBACK BalanceOptsDlgProc(...)`
  - Instance dialog procedure for the per-category options dialog.

## Private Methods

The class privately owns helpers for:

- `ShowBalanceOptions()` - opens the option dialog for data, metadata, or system balance options.
- `SaveBalanceOpts()` - reads dialog controls into `btrfs_balance_opts`.
- `StartBalance()` - launches elevated start operation.
- `RefreshBalanceDlg()` - queries current balance status and updates UI.
- `PauseBalance()` - launches elevated pause/resume operation.
- `StopBalance()` - launches elevated stop operation.

## State Fields

The class stores:

- `balance_status`
- three option structures: `data_opts`, `metadata_opts`, `system_opts`
- active option category `opts_type`
- latest queried balance state `bqb`
- state booleans: `cancelling`, `removing`, `shrinking`, `readonly`
- target path `fn`
- device list pointer `devices`
- constructor context flags `called_from_RemoveDevice` and `called_from_ShrinkDevice`

## Integration

The header depends on Windows types and WinBtrfs IOCTL structures from `../btrfsioctl.h`. Implementation lives in `balance.cpp`, with static dialog thunks forwarding Win32 dialog messages into these instance methods.
