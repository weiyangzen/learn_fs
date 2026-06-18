# File Research: sources/teaching/minix/minix/servers/vfs/utility.c

## Purpose
Provides general VFS utilities for path copying, endpoint validation, supplementary group lookup, and safe userspace data copying.

## Main Entry Points
- `copy_path()` copies pathname data from path-style request messages.
- `fetch_name()` copies a pathname from userspace.
- `isokendpt_f()` validates endpoint-to-process table consistency.
- `in_group()` checks whether a group is in an `fproc` supplementary group list.
- `sys_datacopy_wrapper()` wraps kernel data copies with VM fault handling.

## Control Flow
`copy_path()` handles small embedded path buffers directly and delegates larger paths to `fetch_name()`. Both enforce maximum length and trailing NUL checks.

`sys_datacopy_wrapper()` first tries `sys_datacopy_try`. If it gets `EFAULT`, it asks VM to handle the target memory range via `vm_vfs_procctl_handlemem`, then retries the copy.

## Dependencies
Uses global request state (`job_m_in`, `who_e`, `err_code`), `fproc`, endpoint macros, VM/VFS procctl support, and MINIX data-copy calls.

## Risks and Notes
The wrapper assumes one endpoint is VFS/SELF and asserts that invariant after normalizing `VFS_PROC_NR` to `SELF`. Path functions return `EGENERIC` while setting `err_code`, matching surrounding VFS convention.
