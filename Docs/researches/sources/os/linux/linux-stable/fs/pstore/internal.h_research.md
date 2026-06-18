# File Research: sources/os/linux/linux-stable/fs/pstore/internal.h

## Summary
Internal header shared by pstore core, filesystem, ftrace, and pmsg code.

## Main Responsibilities
- Declare global `kmsg_bytes` and `psinfo`.
- Provide ftrace frontend declarations or no-op stubs depending on `CONFIG_PSTORE_FTRACE`.
- Provide pmsg frontend declarations or no-op stubs depending on `CONFIG_PSTORE_PMSG`.
- Declare record population, file creation, record initialization, and filesystem init/exit helpers.

## Key Interfaces
- `pstore_set_kmsg_bytes()`
- `pstore_get_records()`
- `pstore_get_backend_records()`
- `pstore_put_backend_records()`
- `pstore_mkfile()`
- `pstore_record_init()`
- `pstore_init_fs()` and `pstore_exit_fs()`

## Cross-File Interactions
This header connects `platform.c`, `inode.c`, `ftrace.c`, and `pmsg.c` while keeping optional frontends compilable as stubs.
