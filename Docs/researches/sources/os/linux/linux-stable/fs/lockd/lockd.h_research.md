# File Research: sources/os/linux/linux-stable/fs/lockd/lockd.h

Central internal header for lockd.

Defines:
- Debug facility flags and `LOCKD_VERSION`.
- NLMv4 status constants and internal-only status values.
- `struct nlm_host`: peer identity, RPC client, protocol/version, reclaim/grace state, refcount, lock owner lists, granted/reclaim locks, NSM handle, netns, credentials, and callbacks.
- `struct nsm_handle`: cached statd monitor state, names, address, private cookie, and refcount.
- `struct nlm_lockowner`: per-host synthetic pid mapping for NFS lock owners.
- `struct nlm_wait`: client-side blocked lock wait object.
- `struct nlm_rqst`: client/server RPC request storage.
- `struct nlm_file`: server-side file handle with VFS files, shares, blocks, lock counts, and mutex.
- `struct nlm_block`: server-side blocked lock state and retry/deferred request metadata.

Declares:
- Client procedures, async calls, reclaim, blocking/grant helpers, and cookie generation.
- Host cache lookup/release/bind/rebind/shutdown and reboot handling.
- NSM monitor/unmonitor and handle lookup/release.
- Server-side lock/file/share/resource functions.
- NLM service dispatch and lock manager operations.

Important inline helpers:
- Address accessors for peer/source sockaddr.
- `nlmsvc_file_file()` and inode helpers.
- Privileged local requester checks for IPv4/IPv6 loopback and source ports <=1023.
- `nlm_compare_locks()` compares file, pid, owner, range, and type, treating unlock type as wildcard.
- `lockd_set_file_lock_range4()` converts NLMv4 offset/length to kernel lock range with overflow/EOF handling.
