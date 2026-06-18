# File Research: sources/os/linux/linux-stable/fs/afs/misc.c

## Summary
Contains miscellaneous error handling for AFS. It maps AFS, VL, UAE, RXKAD, RXGK, and Kerberos abort codes to Linux errno values, and prioritizes accumulated errors when an operation tries multiple endpoints.

## Main Responsibilities
- Converts remote abort codes into local negative errno values.
- Handles legacy VICE special errors and VL server errors.
- Handles unified AFS error-table codes.
- Handles rxrpc security abort codes for RXKAD and RXGK.
- Chooses which error should be reported from a sequence of failures.

## Key APIs
- `afs_abort_to_error()`.
- `afs_prioritise_error()`.

## Important Behavior
`afs_abort_to_error()` maps volume movement and availability errors to errno values used by higher-level retry logic, for example `VMOVED` to `-ENXIO`, `VBUSY` to `-EBUSY`, and `VNOVOL` to `-ENOMEDIUM`.

`afs_prioritise_error()` treats success as final, preserves higher-priority existing errors, records whether any server responded, and converts `-ECONNABORTED` through `afs_abort_to_error()` while marking the cumulative error as an abort.

## State and Synchronization
The file only mutates caller-owned `struct afs_error`; it has no independent locking or global state.

## Risks
Error priority directly affects server rotation and user-visible errno. Incorrect ordering could hide a meaningful remote abort behind a transient network failure, or conversely suppress retryable connectivity information.
