# File Research: sources/local-fs/dlm/libdlm/libdlm.h

## Purpose
Public C API header for `libdlm`.

## Contents
- Replicates minimal kernel-compatible user structs/constants when not building the library, so applications do not need kernel DLM headers.
- Declares library/kernel version functions.
- Declares default lockspace lock/unlock APIs.
- Declares fd dispatch APIs for callers that poll their own fds.
- Declares lockspace lifecycle APIs.
- Declares named-lockspace lock/unlock/deadlock/purge APIs.
- Declares pthread receiver APIs under `_REENTRANT`.
- Defines DLM lock modes, lock flags, lock status block flags, and extra return codes.

## Important Constants
- `DLM_LVB_LEN` is 32.
- User-facing `DLM_LOCKSPACE_LEN` and `DLM_RESNAME_MAXLEN` are 64 when not building libdlm.
- `LKF_WAIT` is userspace-only and used to request synchronous behavior.

## Notes
- `dlm_lshandle_t` is an opaque `void *`.
- Public comments document unused parameters such as parent/range in several APIs.
