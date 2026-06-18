# File Research: sources/local-fs/ocfs2-tools/libo2dlm/libdlm-compat.h

## Purpose

Compatibility header that supplies libdlm API declarations and constants when the system libdlm header is unavailable.

## Main Contents

- Defines DLM lock value block length and, outside `BUILDING_LIBDLM`, resource-name length, `struct dlm_lksb`, LKSb flags, and new-lockspace flags.
- Declares library/kernel version functions.
- Declares default-lockspace APIs: synchronous resource lock/unlock under `_REENTRANT`, async lock/unlock, wait variants, file descriptor retrieval, and dispatch.
- Declares custom lockspace APIs: create/new/open/release/close, fd access, lock/unlock/wait/lockx/deadlock cancel/purge.
- Declares optional pthread initialization/cleanup APIs under `_REENTRANT`.
- Defines lock mode constants from null through exclusive.
- Defines DLM locking flags including noqueue, cancel, convert, value block, deadlock options, persistent, expedite, alternate modes, force unlock, timeout, and userspace wait flag.
- Defines extra DLM return codes `ECANCEL`, `EUNLOCK`, and `EINPROG`.

## Dependencies and Integration

- `libo2dlm/Makefile` symlinks this as `libdlm.h` when `LIBDLM_FOUND` is unset.
- Used to compile O2DLM code against a consistent libdlm surface without requiring external headers.

## Research Notes

- Header is LGPL-licensed, unlike most GPLv2 ocfs2-tools source.
- It declares API compatibility but does not implement libdlm behavior.
