# File Research: sources/os/linux/linux/fs/cachefiles/ondemand.c

## Purpose
Implements CacheFiles on-demand mode, where userspace receives open/read/close requests through `/dev/cachefiles` and supplies data via anonymous per-object file descriptors.

## Main Elements
- Anonymous fd operations: `cachefiles_ondemand_fd_release()`, `cachefiles_ondemand_fd_write_iter()`, `cachefiles_ondemand_fd_llseek()`, and `cachefiles_ondemand_fd_ioctl()`.
- `copen` handling: `cachefiles_ondemand_copen()` completes an open request, records object size, updates cookie data-read flags, and transitions object state to open.
- Recovery: `cachefiles_ondemand_restore()` marks pending requests new again after daemon restart.
- Anonymous fd creation: `cachefiles_ondemand_get_fd()` allocates an object ID, fd, and anon inode file, installs fd payload data, and pins cache unbind.
- Request selection and daemon read: `cachefiles_ondemand_select_req()` skips reopening reads and queues reopen work; `cachefiles_ondemand_daemon_read()` returns the next request message to userspace.
- Request lifecycle: `cachefiles_ondemand_send_req()` allocates requests, atomically enqueues them in the cache xarray, wakes the daemon, waits killably, and handles completion races.
- Request payload builders: open, close, and read initializers.
- Object lifecycle: `cachefiles_ondemand_init_object()`, `cachefiles_ondemand_clean_object()`, `cachefiles_ondemand_init_obj_info()`, `cachefiles_ondemand_deinit_obj_info()`, and `cachefiles_ondemand_read()`.

## Dependencies And Integration
Enabled only with `CONFIG_CACHEFILES_ONDEMAND`. Integrates with the daemon command table, CacheFiles object state, request xarrays, anonymous inodes, CacheFiles direct write helpers, FS-Cache workqueue, and the user ABI in `<linux/cachefiles.h>`.

## Risk Notes
This file is concurrency-sensitive: request enqueueing is paired with daemon shutdown barriers, fd release can race `copen`, read requests can trigger object reopen work, and interrupted waits must either remove or wait for completion of a request. Anonymous fd lifetime pins both object and cache unbind state.
