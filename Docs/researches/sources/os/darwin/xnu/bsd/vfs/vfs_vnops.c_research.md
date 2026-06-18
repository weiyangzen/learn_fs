# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_vnops.c

## Purpose

`vfs_vnops.c` implements the file-table-facing vnode operations for Darwin/XNU: open/create with authorization, close, read/write dispatch, stat translation, ioctl/select, pathconf, kqueue vnode filters, and a small internal `vniodesc` API for kernel code to read regular-file vnodes through a persistent descriptor.

It bridges BSD file descriptors and VFS/VNOP interfaces, layering policy checks, file offset serialization, retry handling, compatibility behavior, and event notification around filesystem-provided VNOPs.

## APIs and Entry Points

- Fileops registration: `vnops` with `.fo_read`, `.fo_write`, `.fo_ioctl`, `.fo_select`, `.fo_close`, and `.fo_kqfilter`.
- Open path: `vn_open()`, `vn_open_modflags()`, `vn_open_auth()`, `vn_open_auth_do_create()`, `vn_open_auth_finish()`.
- Close path: `vn_close()`, `vn_closefile()`.
- I/O helpers: `vn_rdwr()`, `vn_rdwr_64()`, `vn_read_common()`, `vn_read()`, `vn_write()`, `vn_read_swapfile()`.
- Offset locking: `vn_offset_lock()`, `vn_offset_unlock()`.
- Attributes and metadata: `vn_stat()`, `vn_stat_noauth()`, `vn_pathconf()`, `vnode_isauthfs()`.
- Device/control dispatch: `vn_ioctl()`, `vn_select()`.
- Kqueue: `vn_kqfilter()`, `filt_vndetach()`, `filt_vnode()`, `filt_vntouch()`, `filt_vnprocess()`, `filt_vnode_common()`, `vnode_readable_data_count()`, `vnode_writable_space_count()`.
- Kernel descriptor API: `vnio_openfd()`, `vnio_close()`, `vnio_read()`, `vnio_vnode()`.

## Control Flow

`vn_open()` and `vn_open_modflags()` prepare a `vnode_attr` and delegate to `vn_open_auth()`. `vn_open_auth()` chooses between create and lookup modes, rewrites namei flags for open semantics, handles `O_NOFOLLOW_ANY`, `O_RESOLVE_BENEATH`, `O_UNIQUE`, named resource forks, data-protection flags, compound open/create VNOPs, and fallback `VNOP_OPEN()`. It updates caller-visible flags: clearing `O_CREAT` when an existing file is opened and clearing `O_TRUNC` when create/compound open already handled truncation.

Create handling uses `vn_open_auth_do_create()`. It authorizes create when compound operations will not do so internally, calls `vn_create()`, recognizes `EKEEPLOOKING` for compound lookup continuation, updates vnode identity for new nodes, drops parent iocounts, and emits create FSEvents when configured.

Open completion calls `vnode_ref_ext()`, MAC open notification, and `kauth_authorize_fileop()`. Error paths close already-opened vnodes, recycle failed shadow streams, drop iocounts, and retry selected races (`ENOENT` after create lookup, `EREDRIVEOPEN`, or reference failure) with bounded retry/yield behavior.

`vn_close()` handles named stream shadow flushes, special-device reference-drop ordering, HFS last-writer fsync behavior, `VNOP_CLOSE()`, content-modified FSEvents, and final vnode reference release.

`vn_rdwr_64()` builds a one-iovec `uio`, performs optional MAC checks, then dispatches to `VNOP_READ()`/`VNOP_WRITE()` or returns zero-filled data for swap-file reads. The file-table `vn_read()` and `vn_write()` paths serialize shared file offsets unless `FOF_OFFSET` is supplied, acquire vnode iocounts from the file reference, apply syscall I/O flags, and update offsets from actual residuals.

`vn_write()` enforces `RLIMIT_FSIZE`, clips writes that would exceed `INT64_MAX` or file-size limits, sends `SIGXFSZ` when no byte can be written, maps fd flags to `IO_*` flags, updates NFS UBC credentials after successful writes, and breaks parent directory leases when file metadata changes.

`vn_stat()` authorizes read attributes/security, then `vn_stat_noauth()` fetches vnode attributes and translates them into `stat` or `stat64`, including type bits, times, allocation blocks, optional file security data, and privileged handling for generation numbers.

`vn_ioctl()` handles generic `FIONREAD`, `FIONBIO`, `FIOASYNC`, `FIODTYPE`, rejects user attempts at `DKIOCSETBLOCKSIZE` and `FSIOC_AUTH_FS`, blocks selected tty revoke ioctls, and otherwise dispatches special files to `VNOP_IOCTL()`.

`vn_kqfilter()` attaches vnode knotes for regular files, FIFOs, and selected character devices, holding the vnode across the knote lifetime and asking filesystems to monitor begin/end events through `VNOP_MONITOR()`. Filter callbacks compute readability/writability, report revoke as EOF/oneshot, and support touch/process paths that detect recycled vnodes by vid.

## State and Invariants

- File offsets are protected by `FG_OFF_LOCKED`/`FG_OFF_LOCKWANT` in `fg_lflags`; regular-file reads/writes keep offset locking longer than non-regular or swap vnodes.
- Open state tracks `did_create`, `did_open`, `need_vnop_open`, `batched`, and `ref_failed`; these determine whether to call `VNOP_CLOSE()` and whether retry is legal.
- `ndp->ni_dvp` must be cleared/dropped before open proceeds past lookup/create; the code panics if it reaches post-lookup with an uncleared parent vnode.
- Compound open support uses `EKEEPLOOKING` plus `NAMEI_CONTLOOKUP` as an explicit continuation protocol with consistency panics for impossible states.
- For special device vnodes, `vnode_rele_ext()` happens before `VNOP_CLOSE()` so device close code can observe use-count state.
- Kqueue filters hold a vnode reference separate from transient iocounts and guard stale detach/process paths with vnode IDs.

## Dependencies

This file depends on XNU VFS/vnode internals, namei, fileglob/fileproc, UBC, MACF, kauth, FSEvents, kqueue, specfs, fifofs, device switch tables, resource limits, signal delivery, data-protection IOCTLs, and filesystem VNOPs such as `VNOP_COMPOUND_OPEN`, `VNOP_OPEN`, `VNOP_CLOSE`, `VNOP_READ`, `VNOP_WRITE`, `VNOP_IOCTL`, `VNOP_SELECT`, `VNOP_ADVLOCK`, `VNOP_PATHCONF`, and `VNOP_MONITOR`.

It also interacts with named-stream/resource-fork support implemented in `vfs_xattr.c`, notably `vnode_flushnamedstream()` and shadow-stream flags.

## Risks and Edge Cases

- Open/create is race-heavy: create races, unlink races, NFS/tty redrive races, compound-open continuation, and vnode reference failures all share cleanup logic.
- `FEXEC` opens retry with `FREAD` for filesystems that reject execute-only opens, which is compatibility-sensitive.
- `O_NOFOLLOW_ANY` cannot be combined with `O_NOFOLLOW`; path-resolution flags are translated into namei flags and must remain consistent with namei semantics.
- Offset clipping for reads/writes around `INT64_MAX` and `RLIMIT_FSIZE` must preserve correct residuals or userspace sees incorrect short I/O behavior.
- Swap-file reads intentionally synthesize zeroes unless encryption-skip flags change the path.
- Kqueue detach/touch/process paths must handle recycled vnodes without leaking vnode holds or using stale pointers.
- The ioctl path deliberately denies some operations from userspace even if a filesystem/device VNOP might accept them.

## Research Notes

The entire 2,392-line file was read. No per-file output was generated separately in this pass.
