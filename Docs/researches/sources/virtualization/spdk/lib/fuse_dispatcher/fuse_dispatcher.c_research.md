# File Research: sources/virtualization/spdk/lib/fuse_dispatcher/fuse_dispatcher.c

`fuse_dispatcher.c` implements SPDK’s deprecated FUSE dispatcher bridge between Linux FUSE request wire structures and the SPDK `fsdev` API. It owns dispatcher creation/deletion, per-channel fsdev channel binding, request parsing, FUSE protocol negotiation, opcode dispatch, output formatting, and async completion lifetime management.

The dispatcher tracks an opened `spdk_fsdev_desc`, the fsdev thread, negotiated protocol version, request-source architecture, root file object, event callback, and fsdev name. Per-dispatcher channels wrap `spdk_fsdev_get_io_channel()` channels. A global `spdk_fuse_mgr` provides a shared mempool for `struct fuse_io` objects, reference-counted across dispatcher instances under a pthread mutex.

The file translates FUSE node IDs and file handles to SPDK pointers. Root maps to `FUSE_ROOT_ID`; other inode values are pointer-cast `spdk_fsdev_file_object` values. File handles are similarly pointer-cast `spdk_fsdev_file_handle` values. This makes the dispatcher tightly coupled to in-process fsdev object lifetimes rather than stable kernel inode identities.

Request parsing is iovec-offset based. Helpers walk input and output iovec arrays, reserve the output header, decode string arguments in place, and copy or directly fill output payloads. Completion helpers fill `fuse_out_header`, preserve the request unique ID, enforce negative error conventions, free the `fuse_io` before invoking the caller completion callback, and special-case `FORGET`/`BATCH_FORGET` as no-reply requests.

The FUSE protocol handlers cover lookup, forget, getattr/setattr, readlink/symlink, mknod/mkdir/unlink/rmdir, rename/rename2, link, open/create, read/write, statfs, release/fsync/flush, xattr get/set/list/remove, init/destroy, opendir/readdir/readdirplus/releasedir/fsyncdir, flock-style locking, interrupt/abort, fallocate, batch forget, and copy-file-range. Unsupported handlers return `-ENOSYS` for GETLK, SETLKW, ACCESS, BMAP, IOCTL, POLL, SETUPMAPPING, REMOVEMAPPING, and SYNCFS.

`FUSE_INIT` negotiates major/minor protocol behavior, supports legacy input/output struct sizes, advertises selected capabilities such as async read, auto invalidation, async DIO, atomic truncate, flock locks, readdirplus, export support, big writes, and optional writeback cache, then mounts the fsdev. If preparing the init reply fails after mount, the code rolls back by issuing `spdk_fsdev_umount()` and retries rollback initiation if fsdev I/O objects are temporarily unavailable.

Architecture support is limited to translating selected open flags between native, x86/x86_64, and ARM/ARM64 layouts. Other integer endian conversion helpers are identity functions, so this is not a general cross-endian FUSE bridge.

Creation opens the named fsdev, creates the shared `FUSE_disp_ios` mempool on first use, registers an SPDK io_device using an offset pointer derived from the dispatcher allocation, and walks all existing dispatcher channels to acquire fsdev I/O channels. Create failure paths close fsdev, free the dispatcher, and unwind channel acquisition. Delete walks channels to put fsdev channels, posts fsdev close back to the original fsdev thread, unregisters the io_device, frees the dispatcher, and releases the global mempool when the last dispatcher is gone.

Fsdev remove events trigger a for-each-channel pass that drops fsdev channels and then calls the dispatcher event callback with `SPDK_FUSE_DISP_EVENT_FSDEV_REMOVE`, preventing later submissions from using stale channels.

Research notes: the most sensitive areas are pointer-as-inode lifetime assumptions, iovec offset accounting, protocol-version struct sizing, `FORGET` no-reply completion paths, and async teardown ordering. The file also explicitly logs a deprecation notice: the `fuse_dispatcher` library is being removed in `v26.09`.
