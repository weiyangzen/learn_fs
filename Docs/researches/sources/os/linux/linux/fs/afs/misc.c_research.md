# File Research: sources/os/linux/linux/fs/afs/misc.c

## Purpose
Provides shared error translation and error-prioritization logic for AFS operations.

## Main Responsibilities
- Maps AFS abort codes, VL server aborts, Unified AFS Error codes, RXKAD/RXGK authentication errors, and generic Rx errors to Linux negative errno values.
- Accumulates and prioritizes errors from multi-server or multi-address operation attempts.

## Key Functions and Data
- `afs_abort_to_error()` converts protocol abort codes to Linux errors.
- `afs_prioritise_error()` updates `struct afs_error` with a preferred cumulative error, response flag, and abort classification.

## Important Details
- Volume and VL errors are mapped to conventional filesystem/network errno values such as `-ENOMEDIUM`, `-ENOSPC`, `-EDQUOT`, `-EBUSY`, and `-ENXIO`.
- Authentication failures map to key errors such as `-EKEYREJECTED`, `-EKEYEXPIRED`, or `-ENOPKG`.
- Prioritization prefers more informative responded/abort errors over transport failures and preserves higher-priority local/network failures according to the fallthrough chain.
- `-ECONNABORTED` is converted through `afs_abort_to_error()` and marks the cumulative error as an abort.
