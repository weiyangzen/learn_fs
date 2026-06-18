# File Research: sources/windows/winbtrfs/src/shellext/iconoverlay.h

Read status: complete, 60 lines.

This header declares `BtrfsIconOverlay`, the COM object implementing `IShellIconOverlayIdentifier`.

Key declarations:
- Constructor initializes refcount and increments `objs_loaded`.
- Destructor decrements `objs_loaded`.
- Implements `QueryInterface`, `AddRef`, `Release`, `GetOverlayInfo`, `GetPriority`, and `IsMemberOf`.
- Stores only a private interlocked refcount.

Integration:
- Implemented in `iconoverlay.cpp`.
- Instantiated through `FactoryIconHandler`.
- Registered by `main.cpp`.

Risk and maintenance notes:
- Manual COM lifetime pattern matches the other shell extension classes.
