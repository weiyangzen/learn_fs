# File Research: sources/os/linux/linux/fs/dlm/lockspace.h

## Role

`lockspace.h` declares the internal lockspace lifecycle and lookup API implemented by `lockspace.c`.

## Constants

`DLM_LSFL_FS` marks a kernel/filesystem lockspace user and enables direct BAST/CAST callbacks. The comment notes it is an internal lockspace flag intended for future removal.

## Exposed Functions

- `dlm_lockspace_init()` and `dlm_lockspace_exit()` initialize/tear down global lockspace infrastructure.
- `dlm_find_lockspace_global(uint32_t id)` finds by global lockspace id and takes a transient reference.
- `dlm_find_lockspace_local(void *id)` takes a reference on a local lockspace pointer.
- `dlm_find_lockspace_device(int minor)` finds a lockspace by device minor.
- `dlm_put_lockspace(struct dlm_ls *ls)` drops a transient lockspace reference.
- `dlm_stop_lockspaces()` stops all running lockspaces when userspace control is gone.
- `dlm_new_user_lockspace()` creates a userspace lockspace.

Kernel/filesystem creation through `dlm_new_lockspace()` is implemented in `lockspace.c` but is exported through broader DLM headers, not this internal header.

## Research Notes

The header exposes only lifecycle and lookup primitives. The heavier `struct dlm_ls` definition remains in `dlm_internal.h`, and release/create variants needed by external users are declared through the public DLM API headers.
