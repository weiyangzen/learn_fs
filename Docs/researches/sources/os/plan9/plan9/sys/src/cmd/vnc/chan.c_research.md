# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/chan.c

User-space emulation of core Plan 9 `Chan`, reference, and canonical-name helpers for the VNC file-server environment.

Key responsibilities:
- Allocates, clones, closes, and frees `Chan` structures.
- Dispatches close to the owning device table.
- Implements locked `Ref` increment/decrement.
- Manages reference-counted `Cname` strings with copy-on-write extension.
- Cleans canonical names, including special `#` device paths.
- Provides directory assertion via `isdir()`.

Important behavior:
- `cclone()` delegates to the device walk method with zero names and shares the original channel name.
- `addelem()` elides `.` and canonicalizes after `..`.
- `cclose()` tolerates device close errors through the local `waserror` mechanism before freeing the channel.

Risks:
- Reference lifecycle is manual and shared with device implementations.
- `Cname.ref > 1` copy-on-write reads the ref without locking.
