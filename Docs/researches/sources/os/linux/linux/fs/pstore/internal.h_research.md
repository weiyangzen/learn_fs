# File Research: sources/os/linux/linux/fs/pstore/internal.h

## Role

Internal pstore header connecting filesystem, platform, ftrace, pmsg, and backend record code.

## Contents

- Declares global `kmsg_bytes` and active backend pointer `psinfo`.
- Provides ftrace frontend prototypes or no-op stubs depending on `CONFIG_PSTORE_FTRACE`.
- Provides pmsg frontend prototypes or no-op stubs depending on `CONFIG_PSTORE_PMSG`.
- Declares core helpers:
  - `pstore_set_kmsg_bytes`
  - `pstore_get_records`
  - `pstore_get_backend_records`
  - `pstore_put_backend_records`
  - `pstore_mkfile`
  - `pstore_record_init`
  - `pstore_init_fs`
  - `pstore_exit_fs`

## Research Notes

The header intentionally keeps optional frontend call sites simple by providing stubs when features are disabled.
