# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/internal.c

This file contains RGW FSAL internal helpers shared by module/export and handle operations. Its main responsibilities are converting librgw negative POSIX-style errors into `fsal_status_t` and constructing/destructing private RGW object handles.

The key API is `rgw2fsal_error(int)`, which stores the positive POSIX errno in `minor` and maps common conditions to FSAL majors such as `ERR_FSAL_NOENT`, `ERR_FSAL_IO`, `ERR_FSAL_ACCESS`, `ERR_FSAL_EXIST`, `ERR_FSAL_STALE`, and `ERR_FSAL_DELAY`. `construct_handle` allocates a `struct rgw_handle`, attaches the librgw `rgw_file_handle`, copies upcall ops from the export, initializes the embedded public object handle with `fsal_obj_handle_init`, assigns `RGWFSM.handle_ops`, fills fsid/fileid from `struct stat`, and returns it to the caller. `deconstruct_handle` finalizes the public handle and frees the private allocation.

Control flow is intentionally small: callers obtain an RGW handle/stat from librgw, call `construct_handle`, then later call `release` in `handle.c`, which may release the librgw file-handle reference and then call `deconstruct_handle`. This file does not own persistence; it creates in-memory wrappers around persistent RGW objects.

Dependencies are Ganesha FSAL types, `fsal_convert`, common allocation helpers, and the declarations in `internal.h`. The error mapping is an integration point between librgw and every FSAL operation that returns provider errors.

Risks are mostly semantic drift: if librgw adds important negative errors, unmapped cases become `ERR_FSAL_SERVERFAULT`; `EBADF` is mapped to `ERR_FSAL_NOT_OPENED` even though comments note access-mode ambiguity; `construct_handle` does not check allocation failure because Ganesha allocation helpers are expected to abort. Test signals should verify representative error translations and ensure constructed handles get correct type, fsid, fileid, ops vector, export pointer, and cleanup behavior.
