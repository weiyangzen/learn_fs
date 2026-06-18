# File Research: sources/os/plan9/9front/sys/src/9/cycv/ltrap.s

Cyclone V ARM exception vector and syscall/trap entry assembly.

Key responsibilities:
- Defines ARM exception vectors.
- Handles instruction abort, generic exceptions, and SVC/syscall entry.
- Saves registers and status into `Ureg` layout.
- Restores `Mach`/`Proc` context from TPIDRPRW.
- Calls C `trap()` or `syscall()`.
- Restores user or kernel state and returns from exception.

Important behavior:
- Differentiates abort mode and general exception mode when saving PSR/type.
- Uses CPS mode switches and banked register restore for user returns.

Dependencies:
- `mem.h`, `io.h`, C trap/syscall handlers, and `Ureg` layout.
