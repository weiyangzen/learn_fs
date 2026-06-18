# File Research: sources/windows/winbtrfs/src/shellext/factory.h

Read status: complete, 68 lines.

This header declares the COM `Factory` class and factory type enum.

Key declarations:
- `factory_type` identifies which shell extension object the factory should create.
- `Factory` implements `IClassFactory`.
- Constructor initializes refcount to zero, sets type to `FactoryUnknown`, and increments global `objs_loaded`.
- Destructor decrements `objs_loaded`.
- `AddRef` and `Release` use interlocked operations; `Release` deletes on zero.
- Public `type` is assigned by `DllGetClassObject`.

Integration:
- Implemented in `factory.cpp`.
- Used by `main.cpp` for all registered COM class IDs.
- Shares `objs_loaded` with all shell extension COM classes to support `DllCanUnloadNow`.

Risk and maintenance notes:
- Public mutable `type` is simple but requires callers to set it before use. `DllGetClassObject` does that immediately.
