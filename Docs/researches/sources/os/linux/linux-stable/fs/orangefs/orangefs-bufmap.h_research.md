# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-bufmap.h

## Scope

This header declares the OrangeFS shared buffer-map interface.

## APIs Declared

- Bufmap lifecycle and sizing: `orangefs_bufmap_size_query()`, `orangefs_bufmap_initialize()`, `orangefs_bufmap_finalize()`, `orangefs_bufmap_run_down()`.
- Slot allocation: `orangefs_bufmap_get()`, `orangefs_bufmap_put()`, `orangefs_readdir_index_get()`, `orangefs_readdir_index_put()`.
- Data movement: `orangefs_bufmap_copy_from_iovec()`, `orangefs_bufmap_copy_to_iovec()`.

## Dependencies And Role

- Consumed by file I/O, readdir, and request-device code.
- Uses `struct ORANGEFS_dev_map_desc` from the OrangeFS device protocol headers.
