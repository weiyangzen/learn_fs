# File Research: sources/windows/winbtrfs/src/shellext/volpropsheet.h

## Purpose
Declares the Explorer volume property sheet COM class and drive-letter dialog helper.

## Main Components
- `BtrfsVolPropSheet`: implements `IShellExtInit` and `IShellPropSheetExt`.
  - Constructor initializes COM refcount-related state, increments global loaded object count, and clears device/balance state.
  - Destructor releases storage medium, frees device buffer, decrements global loaded object count, and deletes balance helper.
  - Implements `QueryInterface`, `AddRef`, `Release`, `Initialize`, `AddPages`, and `ReplacePage`.
  - Declares methods for usage, device list, scrub, drive-letter, device stats, and stats reset workflows.
- Public state used by dialogs:
  - `btrfs_device* devices`
  - `bool readonly`
  - `BtrfsBalance* balance`
  - `BTRFS_UUID uuid`
  - `bool uuid_set`
- Private state:
  - COM reference count.
  - `ignore` flag determining whether to add the page.
  - Explorer `STGMEDIUM`.
  - selected path `fn`.
  - active stats device ID.
- `BtrfsChangeDriveLetter`: helper for the drive-letter modal dialog.
  - Stores parent window, target volume path, and available letters.
  - Provides `show`, `DlgProc`, and private `do_change`.

## Dependencies
Includes Shell interfaces, WinBtrfs ioctl/header files, and related shell extension headers `balance.h` and `scrub.h`.

## Notable Behavior
`BtrfsVolPropSheet` is a COM object with manual reference counting and global DLL lifetime integration through `objs_loaded`. Dialog procedures access the object through `GWLP_USERDATA` and operate directly on its shared state.
