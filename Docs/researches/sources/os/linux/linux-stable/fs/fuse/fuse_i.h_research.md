# File Research: sources/os/linux/linux-stable/fs/fuse/fuse_i.h

## Purpose

`fuse_i.h` is the main internal FUSE header. It defines core FUSE kernel structures, connection feature state, request objects, inode/file private data, mount context data, helper functions, constants, and cross-file prototypes.

## Main Responsibilities

- Defines default request/page limits and global module parameters.
- Defines private inode, file, request, queue, device, mount, and connection structures.
- Defines FUSE inode state bits and request state bits.
- Defines request argument containers and page/folio descriptors.
- Declares helpers implemented across `dir.c`, `file.c`, `inode.c`, device code, DAX, ioctl, xattr, ACL, readdir, iomode, backing, and passthrough code.
- Provides inline accessors for FUSE mount/connection/inode/file state.
- Provides no-op or conditional declarations for optional DAX, passthrough, and sysctl functionality.

## Core Data Structures

`struct fuse_inode` extends Linux `struct inode` with:
- FUSE nodeid and lookup count.
- Pending forget message.
- Attribute timeout, invalid mask, original mode/ino, birth time, attribute version.
- Regular-file cache/writeback state: write file list, queued writes, write counter, page-cache I/O counter, wait queues.
- Directory readdir-cache state.
- Per-inode state bits and serialization locks.
- Optional DAX, submount, and passthrough state.

Important inode state bits include:
- `FUSE_I_ADVISE_RDPLUS`
- `FUSE_I_INIT_RDPLUS`
- `FUSE_I_SIZE_UNSTABLE`
- `FUSE_I_BAD`
- `FUSE_I_BTIME`
- `FUSE_I_CACHE_IO_MODE`
- `FUSE_I_EXCLUSIVE`

`struct fuse_file` stores:
- Mount pointer, server file handle, kernel handle, nodeid, refcount, and `FOPEN_*` flags.
- Writeback list entry.
- Readdir stream/cache position.
- Poll rb-tree node and wait queue.
- Cached/uncached I/O mode state.
- Optional passthrough file/cred.
- Flock marker.

`struct fuse_conn` is the connection-wide state holder:
- Global locks, refcount, epoch, user/group/userns/pidns.
- Request queues and device lists.
- Background request throttling.
- INIT/connected/aborted/error state.
- Negotiated feature bits.
- Capability fallback bits such as `no_open`, `no_fsync`, `no_lseek`, `no_statx`, etc.
- Attribute/evict version counters.
- DAX, passthrough, io_uring, timeout, poll, and syncfs state.
- List of `struct fuse_mount` objects sharing the connection.

`struct fuse_mount` binds a superblock to a shared `fuse_conn`, supporting submounts and shared connections.

## Request Model

`struct fuse_args` describes high-level request input/output arguments and page behavior flags:
- ordinary scalar args,
- page-backed input/output,
- variable-length output,
- zeroing/replacement behavior,
- background completion callback,
- credential/force/may-block behavior,
- vmalloc kvec invalidation support.

`struct fuse_req` is the queued request object with input/output headers, flags, wait queue, mount pointer, optional transport buffers, and creation time.

Request flags describe lifecycle and transport state:
- waiting, pending, sent, finished,
- background, force, reply,
- interrupted, aborted, locked,
- async and io_uring.

`struct fuse_io_priv` aggregates multi-request direct-I/O completion state.

## Queue and Device Model

`struct fuse_iqueue` is the input queue visible to the userspace server/device transport. It contains pending requests, interrupts, forgets, request counter, wait queue, fasync state, and transport-specific callbacks.

`struct fuse_pqueue` tracks processing requests in a hash table and I/O list.

`struct fuse_dev` represents one device instance with refcount, connection pointer, processing queue, and connection device-list entry.

## Feature Negotiation State

`struct fuse_conn` contains negotiated flags for:
- async read and async direct I/O,
- atomic open truncate,
- export support,
- writeback cache,
- parallel directory operations,
- killpriv v1/v2,
- symlink caching,
- big writes,
- auto/explicit invalidation,
- readdirplus,
- POSIX ACLs,
- submounts,
- syncfs,
- init-security/create supplementary groups,
- inode DAX,
- direct-I/O mmap relaxation,
- statx,
- passthrough,
- kvec page transport,
- link support,
- sync init,
- io_uring transport,
- request timeouts.

It also stores optimization fallback flags when operations return `-ENOSYS`.

## Important Inline Helpers

The header provides:
- `get_fuse_mount_super()`, `get_fuse_conn_super()`, `get_fuse_mount()`, `get_fuse_conn()`.
- `get_fuse_inode()` and `get_node_id()`.
- `invalid_nodeid()`.
- attribute/evict version readers.
- stale/bad inode helpers.
- DAX and passthrough helpers.
- `fuse_folios_alloc()` for paired folio/descriptor arrays.
- `fuse_set_zero_arg0()` for operations that need a placeholder first argument.

## Cross-Module Contract

This header ties together:
- `dir.c` for dentries, attributes, permissions, setattr, xattrs/ACLs.
- `file.c` for file I/O and writeback.
- `inode.c` for mount/superblock/inode lifecycle.
- `dev.c` and transport code for request queuing and completion.
- DAX, ioctl, readdir, passthrough, backing, sysctl, and control filesystem modules.

## Edge Cases and Risks

- The connection struct has many feature and fallback bits; code must distinguish negotiated capabilities from `-ENOSYS` runtime fallbacks.
- Inode fields share a union between regular-file and directory-specific cache state, so initialization must match inode type.
- Request argument flags control memory ownership, page pinning, vmalloc flushing, and completion behavior; incorrect combinations can corrupt data or leak refs.
