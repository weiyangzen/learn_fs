# File Research: sources/os/bsd/dragonflybsd/sys/kern/tty_tty.c

## Summary
Indirect driver for `/dev/tty`, the current process controlling terminal. It forwards operations to the session controlling tty vnode.

## Main Responsibilities
- Creates `/dev/tty`.
- Opens/closes the controlling tty vnode once per session using `VCTTYISOPEN`.
- Forwards reads, writes, ioctls, and kqueue filters to the controlling tty vnode.
- Implements `TIOCNOTTY` for non-session-leader processes.
- Rejects `TIOCSCTTY` on `/dev/tty` to avoid recursive controlling-terminal assignment.

## Important Behavior
Open/close paths use vnode holds/refs and retry loops to survive races where the controlling terminal changes or is revoked while locks are being acquired. Read/write use `vget` because the controlling tty reference can disappear while blocked.

If no controlling tty exists, read/write return `EIO`, open returns `ENXIO`, and kqueue installs fallback filters that report generic readiness via `seltrue`.

## Risks
This file is mostly race handling around session tty vnode lifetime. Correctness depends on `P_CONTROLT`, `s_ttyvp`, `VCTTYISOPEN`, vnode locking, and revoke semantics staying aligned.
