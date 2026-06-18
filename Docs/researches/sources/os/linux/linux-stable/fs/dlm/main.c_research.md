# File Research: sources/os/linux/linux-stable/fs/dlm/main.c

## Purpose
`main.c` is the DLM module entry/exit file. It establishes subsystem initialization and teardown ordering.

## Initialization
`init_dlm()` initializes:
1. DLM memory caches.
2. Midcomms/lowcomms data structures.
3. Lockspace subsystem.
4. Config subsystem.
5. Debugfs.
6. User devices.
7. POSIX-lock device.
8. Shared `dlm_wq`.

On failure, it unwinds initialized components in reverse order.

## Exit
`exit_dlm()` destroys `dlm_wq`, exits plock/user/config/lockspace/midcomms/debugfs, and then destroys memory caches.

## Exports
Exports the public kernel DLM API:
- `dlm_new_lockspace`
- `dlm_release_lockspace`
- `dlm_lock`
- `dlm_unlock`

## Notes
The file is ordering-focused rather than protocol-heavy. Destroying `dlm_wq` first ensures pending freeing/callback work is complete before subsystem teardown.
