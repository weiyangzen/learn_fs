# File Research: sources/os/bsd/freebsd-src/sys/kern/tty_tty.c

## Purpose
Implements `/dev/tty` clone behavior, resolving the calling process’s controlling terminal to the backing tty device or falling back to a dummy `ctty` device.

## Core Behavior
- `cttyopen()` always returns `ENXIO`; it is used when no valid controlling tty exists.
- `ctty_clone()` handles devfs clone requests for the name `tty`.
- It checks `curproc` under `proctree_lock` and `dev_lock()`:
  - If the process lacks `P_CONTROLT`, returns `ctty`.
  - If the session has no tty vnode, returns `ctty`.
  - If the vnode was revoked or lacks a device, returns `ctty`.
  - Otherwise returns the controlling tty vnode’s `v_rdev`.
- `ctty_drvinit()` registers the devfs clone event handler and creates the eternal `ctty` device.

## Dependencies
Uses devfs clone event handling, process/session controlling tty state, vnode/device references, and device reference locking.

## Notes and Risks
- This file does not implement normal tty I/O; it only maps `/dev/tty` opens to the right character device.
- The dummy device prevents invalid controlling-terminal lookups from accidentally resolving to stale devices.
