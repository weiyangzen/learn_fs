# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/chan.c

## Role

`chan.c` implements a user-space subset of Plan 9 kernel channel and canonical-name management for the VNC server's synthetic device filesystem.

## Core Behavior

- `newchan()` allocates and initializes a `Chan`.
- `cclose()` decrements channel references, calls the owning device's close method on last close, and frees the channel.
- `cclone()` clones a channel by issuing a zero-element device walk and sharing the canonical name.
- `Ref` helpers `incref()` and `decref()` provide lock-protected reference counting.
- `newcname()`, `cnameclose()`, `addelem()`, and `cleancname()` manage copy-on-write path names.
- `isdir()` validates directory channels and raises `Enotdir`.

## Notable Limitations And Risk Areas

- This is a narrow compatibility layer, not the full Plan 9 kernel name system.
- `cclone()` depends on each `Dev.walk` correctly supporting a zero-name clone operation.
- `addelem()` only normalizes on `..`, so callers rely on earlier path parsing discipline for other cases.
- Device close errors are swallowed after `waserror()`, matching kernel-like cleanup expectations.
