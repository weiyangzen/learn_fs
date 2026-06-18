# File Research: sources/windows/winbtrfs/src/shellext/factory.cpp

Read status: complete, 94 lines.

This file implements the COM class factory used by the shell extension DLL.

Key behavior:
- `Factory::QueryInterface` supports `IUnknown` and `IClassFactory`.
- `Factory::LockServer` returns `E_NOTIMPL`.
- `Factory::CreateInstance` rejects aggregation with `CLASS_E_NOAGGREGATION`.
- It creates a concrete COM object based on `Factory::type`:
  - `FactoryIconHandler` creates `BtrfsIconOverlay`.
  - `FactoryContextMenu` creates `BtrfsContextMenu`.
  - `FactoryPropSheet` creates `BtrfsPropSheet`.
  - `FactoryVolPropSheet` creates `BtrfsVolPropSheet`.
- For each type, it only creates the object if the requested interface is one of the supported shell interfaces.

Integration:
- Used by `DllGetClassObject` in `main.cpp`, which sets the factory type after allocation.
- Pulls in `iconoverlay.h`, `contextmenu.h`, `propsheet.h`, and `volpropsheet.h`.

Risk and maintenance notes:
- Objects are allocated with refcount zero and returned through their own `QueryInterface`, which supplies the initial reference.
- `LockServer` is unimplemented. Shell usage may tolerate this, but a full COM server implementation typically tracks server locks.
