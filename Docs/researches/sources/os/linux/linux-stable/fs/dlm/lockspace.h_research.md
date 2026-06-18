# File Research: sources/os/linux/linux-stable/fs/dlm/lockspace.h

## Purpose
`lockspace.h` declares the lockspace lifecycle API and defines the private filesystem-user flag.

## Exports
- `DLM_LSFL_FS`: internal flag for kernel/filesystem users, enabling direct BAST/CAST callbacks.
- `dlm_lockspace_init()`
- `dlm_lockspace_exit()`
- `dlm_find_lockspace_global()`
- `dlm_find_lockspace_local()`
- `dlm_find_lockspace_device()`
- `dlm_put_lockspace()`
- `dlm_stop_lockspaces()`
- `dlm_new_user_lockspace()`

## Integration
Used by DLM initialization, user-device paths, message receive paths, and filesystem-facing lockspace creation. Kernel callers use the non-header-declared public `dlm_new_lockspace()` from the broader DLM interface, while this header exposes the internal user-lockspace constructor and lookup/refcount helpers.
