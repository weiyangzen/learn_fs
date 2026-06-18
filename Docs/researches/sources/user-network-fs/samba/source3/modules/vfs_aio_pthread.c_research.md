<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aio_pthread.c -->
# sources/user-network-fs/samba/source3/modules/vfs_aio_pthread.c

## Purpose
This VFS module provides thread-pool-backed asynchronous open support for selected create-exclusive opens. It is intentionally narrow: only `O_CREAT|O_EXCL` opens are offloaded, reducing latency for potentially slow creates while avoiding broader path-resolution races.

## Important APIs, Types, And Functions
When `HAVE_OPENAT` and `HAVE_LINUX_THREAD_CREDENTIALS` are available, the core type is `struct aio_open_private_data`, tracked in static `open_pd_list`. Helpers include `find_open_private_data_by_mid`, `aio_open_handle_completion`, `aio_open_worker`, `aio_open_do`, `opd_free`, `create_private_open_data`, `opd_inflight_destructor`, `open_async`, and `find_completed_open`. The registered VFS hook is `aio_pthread_openat_fn`.

## Control Flow
`aio_pthread_openat_fn` first rejects unsupported resolve flags, named streams, missing threadpool, SMB multichannel, pathref opens, non-create opens, non-exclusive creates, and `RESOLVE_NO_XDEV` cases needing retry through other open paths. If async open is disabled or ineligible, it calls `SMB_VFS_NEXT_OPENAT`. For eligible first-pass opens, it snapshots connection, names, credentials, dir fd, flags, mode, MID, and initial allocation size, then queues `aio_open_worker` on Samba's pthreadpool and returns `EINPROGRESS`. Completion clears the in-flight destructor, reschedules the deferred SMB open by MID, and stores the returned fd/errno. A later reentrant open for the same MID returns the completed fd.

## State And Persistence
Outstanding opens are stored in process memory in `open_pd_list` and allocated under the connection so teardown can mark abandoned work. No durable state is written. Worker threads set Linux thread credentials before `openat`; optional `fallocate` sets initial allocation size as an optimization.

## Dependencies And Integration Points
Dependencies include Samba pthreadpool/tevent integration, Linux thread credentials, `openat`, deferred SMB open scheduling, SMB MID tracking, `files_struct`/`smb_filename` copying, and loadparm option `aio_pthread:aio open`. It is registered as `aio_pthread`.

## Risks
The module is disabled for multichannel because MID-to-connection assumptions are not yet compatible. If a supposedly completed open is still in progress on reentry, the module panics, treating it as an open timeout. Connection teardown while a worker is in flight relies on a destructor that prevents freeing and later schedules an error response. Thread creation `EAGAIN` falls back to synchronous processing under restored user credentials.

## Test Signals
Useful tests include eligible `O_CREAT|O_EXCL` async opens, ineligible fallback paths, threadpool unavailable, connection teardown during in-flight open, worker credential failure, `EAGAIN` fallback, initial allocation-size optimization, and `RESOLVE_NO_XDEV` retry behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aio_pthread.c -->
