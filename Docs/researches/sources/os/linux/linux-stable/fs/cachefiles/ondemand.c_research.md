# File Research: sources/os/linux/linux-stable/fs/cachefiles/ondemand.c

This optional file implements CacheFiles on-demand read mode, where userspace receives cache miss/open/read/close requests and can write fetched data through anonymous object fds.

Core protocol:
- Requests are stored in `cache->reqs` xarray and marked `CACHEFILES_REQ_NEW` until delivered to userspace.
- Each request contains a `cachefiles_msg` with opcode, length, msg id, object id, and opcode-specific payload.
- Object ids are allocated from `cache->ondemand_ids`.
- Userspace reads requests through `/dev/cachefiles`, replies to open with `copen`, completes reads with `CACHEFILES_IOC_READ_COMPLETE`, and writes fetched data to the anonymous fd.

Anonymous fd operations:
- `cachefiles_ondemand_get_fd()` allocates an object id, unused fd, and anon inode file using `cachefiles_ondemand_fd_fops`; it embeds the fd in the open message payload.
- `cachefiles_ondemand_fd_write_iter()` writes userspace-provided data into the backing cache file after preparing aligned cache space.
- `cachefiles_ondemand_fd_llseek()` delegates seeks to the backing file.
- `cachefiles_ondemand_fd_ioctl()` handles `CACHEFILES_IOC_READ_COMPLETE` by locating and completing the matching read request.
- `cachefiles_ondemand_fd_release()` marks the object closed, completes pending close requests, removes object id, drops object and unbind refs.

Request handling:
- `cachefiles_ondemand_send_req()` allocates and initializes a request, atomically checks cache liveness and enqueues it, wakes daemon pollers, waits killably for completion, handles interruption by trying to finish the request, and resets open state on failure.
- Memory barriers pair with `cachefiles_flush_reqs()` to avoid orphaning requests during daemon shutdown.
- `cachefiles_ondemand_daemon_read()` fairly selects new requests, skips reopening reads as needed, creates fds for open requests, copies messages to userspace, installs fds, and auto-finishes close/error requests.

Open/close/read commands:
- `cachefiles_ondemand_copen()` parses `copen <id>,<cache_size>`, removes the matching open request, updates cookie object size and no-data flag, transitions object state to open, and completes the request.
- `cachefiles_ondemand_restore()` re-marks existing requests as new after userspace daemon recovery.
- `cachefiles_ondemand_read()` sends a read request with offset and length.
- `cachefiles_ondemand_clean_object()` sends close, marks dropping, completes all requests for the object with `-EIO`, erases them, and cancels reopen work.

Reopen behavior:
- If a read request targets a closed object, `cachefiles_ondemand_select_req()` moves the object to reopening state and queues `ondemand_object_worker()`, which sends a new open request.
- Reads for objects already reopening are skipped until open completes.

Object metadata:
- `cachefiles_ondemand_init_obj_info()` allocates per-object info only in on-demand mode.
- `cachefiles_ondemand_init_object()` sends an open request unless the object is already open.
- Open request payload contains volume key and cookie key and requires `FSCACHE_ADV_WANT_CACHE_SIZE`.

Key risks controlled by the implementation:
- It avoids stale msg id reuse with cyclic xarray allocation.
- It handles daemon death by completing and erasing outstanding requests.
- It guards against anonymous fd being closed before `copen`.
- It waits for reopen work during object cleanup to prevent use-after-free.
