# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/dat.c

This file defines KFS global variables, default filesystem/device tables, tag names, and error strings.

Key contents:
- Global uid/gid storage, main lock, boot time, lock table, config, console state, active channel, service name, process names, and block-size globals.
- `filesys` default array with one filesystem named `main` on `Devwren`.
- `devnone` sentinel device.
- `devcall` dispatch table mapping `Devwren` to `wren*` operations.
- `tagnames` for block tag diagnostics.
- `errstring` mapping KFS internal error codes to protocol error strings.

Role:
- Central registry for the single-device KFS build.
- Used by nearly every KFS source file via extern declarations in `dat.h`.

Notable details:
- `writeallow`, `wstatallow`, `allownone`, `noatime`, and `writegroup` are declared elsewhere but exposed through `dat.h`.
- Error strings are shared by 9P1, 9P2, console, and command output.
