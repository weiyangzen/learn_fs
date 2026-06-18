# File Research: sources/windows/winbtrfs/src/shellext/contextmenu.h

Read status: complete, 83 lines.

This header declares `BtrfsContextMenu`, the COM object implementing `IShellExtInit` and `IContextMenu` for WinBtrfs Explorer commands.

Key declarations:
- Constructor initializes the object as ignored until successful initialization, clears `STGMEDIUM` state, clears the UAC icon handle, disables snapshot permission, and increments global `objs_loaded`.
- Destructor releases clipboard/selection `STGMEDIUM` data when owned, deletes the generated UAC bitmap, and decrements `objs_loaded`.
- Implements COM lifetime methods `QueryInterface`, `AddRef`, and `Release`.
- Implements `Initialize`, `QueryContextMenu`, `InvokeCommand`, and `GetCommandString`.
- Private state records selected/background mode, target path, menu suppression, snapshot eligibility, and UAC icon bitmap.
- Private helpers are `reflink_copy` and `get_uac_icon`.

Integration:
- Implemented in `contextmenu.cpp`.
- Created by `Factory::CreateInstance` when the factory type is `FactoryContextMenu`.
- `objs_loaded` is shared with `DllCanUnloadNow` in `main.cpp`.

Risk and maintenance notes:
- Manual COM refcounting starts at zero and depends on factory `QueryInterface` returning the initial reference.
- `STGMEDIUM` ownership is tracked by `stgm_set`; future initialization paths must maintain it carefully to avoid leaks or double release.
