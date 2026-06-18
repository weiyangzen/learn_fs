# File Research: sources/windows/winbtrfs/src/shellext/recv.h

## Purpose
Declares the receive-side shell extension class and helper cache structure used by `recv.cpp`.

## Main Components
- `subvol_cache`: stores a received or discovered subvolume identity:
  - `BTRFS_UUID uuid`
  - `uint64_t transid`
  - `wstring path`
- `BtrfsRecv`: stateful receive controller for GUI and quiet operation.

## Public Interface
- Constructor initializes all handles to invalid/null states, clears paths/cache, and sets counters/flags.
- Destructor clears the clone/subvolume cache.
- `Open(HWND hwnd, const wstring& file, const wstring& path, bool quiet)`: launches receive.
- `recv_thread()`: worker implementation used by GUI thread wrapper or quiet mode.
- `RecvProgressDlgProc(...)`: progress dialog message handler.

## Private Interface
Declares command handlers for all supported Btrfs send stream operations: subvolume, snapshot, create, rename, link, unlink, rmdir, xattr, write, clone, truncate, chmod, chown, and utimes. Also declares TLV lookup, cache insertion, and core `do_recv`.

## State
Tracks stream path, destination path, current subvolume path, active directory/master/write handles, progress dialog handle, received count, current subvolume UUID/transid, cancellation/running flags, and UUID/transid-to-path cache.

## Dependencies
Includes `<shlobj.h>` and `../btrfs.h`; relies on `win_handle` from `shellext.h` in method signatures even though the header itself is normally included after or with `shellext.h`.

## Notable Behavior
The class owns operational state across the entire receive session. It is not designed for concurrent receive operations in the same instance.
