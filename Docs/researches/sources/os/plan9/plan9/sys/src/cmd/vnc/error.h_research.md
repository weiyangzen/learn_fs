# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/error.h

Extern declarations for Plan 9-style error string globals used by the VNC compatibility/device code.

Key contents:
- Declares common kernel error strings such as `Enonexist`, `Eperm`, `Ebadarg`, `Einuse`, `Eshort`, `Ebadstat`, and many others.
- Mirrors the definitions in `errstr.h`.

Role:
- Lets device code call `error(Eperm)` and related Plan 9 idioms while linking against user-space string definitions.

Risks:
- This header must stay consistent with `errstr.h`.
