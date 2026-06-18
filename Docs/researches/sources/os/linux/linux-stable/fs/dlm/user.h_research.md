# File Research: sources/os/linux/linux-stable/fs/dlm/user.h

## Purpose
`user.h` declares userspace-device integration points for DLM.

## Exports
- `dlm_purge_lkb_callbacks()`
- `dlm_user_add_ast()`
- `dlm_user_init()`
- `dlm_user_exit()`
- `dlm_device_deregister()`
- `dlm_user_daemon_available()`

## Notes
`dlm_purge_lkb_callbacks()` is declared here but is not defined in the listed `user.c`; it may be implemented elsewhere in DLM or be a stale declaration.
