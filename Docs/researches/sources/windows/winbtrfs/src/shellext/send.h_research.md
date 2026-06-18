# File Research: sources/windows/winbtrfs/src/shellext/send.h

## Purpose
Declares the `BtrfsSend` GUI/controller class for exporting Btrfs send streams.

## Main Components
- Constructor initializes send state, destination buffer, handles, source path, and incremental flag.
- Destructor frees the heap send buffer if present.
- Public methods:
  - `Open(HWND hwnd, WCHAR* path)`: opens the send dialog for a source subvolume.
  - `SendDlgProc`: dialog message handler.
  - `Thread`: worker implementation.
- Private methods:
  - `StartSend`, `Browse`, `BrowseParent`, `AddClone`, `RemoveClone`.

## State
- `started`: whether a send is active.
- `incremental`: whether a parent subvolume is required.
- `file[MAX_PATH]`: destination stream path.
- `closetext[255]`: original Cancel/Close button text.
- `dirh`, `stream`, `thread`: active handles.
- `hwnd`: owning dialog.
- `subvol`: source subvolume path.
- `buf`: send buffer allocated in worker.
- `clones`: selected clone source paths.

## Dependencies
Includes `../btrfs.h`; requires declarations from `shellext.h` and Win32 headers in implementation context.

## Notable Behavior
The class is stateful and dialog-oriented. It keeps live handles as members so cancellation can close/delete the active operation from the UI thread.
