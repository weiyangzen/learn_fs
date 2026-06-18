# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fifofs/fifovnops.c

## Role

Implements FIFOFS vnode operations for STREAMS-backed FIFOs and pipes. It is the main VOP layer for opening, closing, reading, writing, polling, attributes, ACL delegation, and stream ioctl handling for `VFIFO` nodes.

## Main Behavior

- Defines `fifo_vnodeops_template`, wiring FIFOFS operations into illumos VFS: open, close, read, write, ioctl, getattr, setattr, access, create, fsync, inactive, fid, rwlock/rwunlock, seek, realvp, poll, pathconf, and security attribute operations.
- `fifo_open()` synchronizes reader and writer opens with `fn_rcnt`, `fn_wcnt`, `fn_rsynccnt`, `fn_wsynccnt`, `FIFOSYNC`, `FIFOROCR`, and `FIFOWOCR`. Blocking opens wait for the opposite end; nonblocking writer opens can fail with `ENXIO`.
- `fifo_close()` serializes open/close teardown with `flk_ocsync`, cleans locks/shares/STREAMS state, sends `M_HANGUP`, wakes sleeping peers, handles named pipe unmount via `nm_unmountall()`, and flushes fast-mode buffers.
- `fifo_read()` uses fast-mode in-memory message blocks when `FIFOFAST` is set, otherwise delegates to `strread()`. It handles EOF/no-writer cases, `FNDELAY`/`FNONBLOCK`, signal interruption, access time updates, and writer wakeups under high-water pressure.
- `fifo_write()` fast-paths writes into the peer fifonode’s message queue, enforces `Fifohiwat` flow control, splits oversized writes into `PIPE_BUF` chunks, wakes readers, updates mtime/ctime, and sends `SIGPIPE`/`EPIPE` when readers disappear.
- `fifo_fastioctl()` services selected ioctl operations without leaving fast mode, including `I_NREAD`, `FIORDCHK`, `I_PEEK`, `FIONREAD`, `I_FLUSH`, `I_CANPUT`, and `_I_GETPEERCRED`. Unsupported STREAMS-sensitive ioctls call `fifo_fastoff()` and fall back to `fifo_strioctl()`.
- `fifo_poll()` implements fast-mode readiness and hangup reporting, including `POLLET` registration via stream poll lists, and delegates to `strpoll()` in STREAMS mode.
- Attribute operations proxy to `fn_realvp` for named FIFOs and synthesize metadata for anonymous pipes.

## Important Details

- `tsol_fifo_access()` enforces Trusted Extensions cross-zone write policy for named FIFOs by comparing the caller zone with the FIFO’s zone path owner.
- Fast-mode/STREAMS-mode conversion is guarded by `FIFOSTAYFAST` and `FIFOWAITMODE` through `fifo_stayfast_enter()` and `fifo_stayfast_exit()`.
- `fifo_inactive()` coordinates vnode count removal with `ftable_lock`, removes real-vnode-backed FIFOs from the FIFO table, releases underlying vfs/vnode references, and frees pipe/fnode cache allocations when the shared lock refcount drops to zero.
- `fifo_fsync()` propagates newer FIFO access/modify times to the underlying real vnode before calling its `VOP_FSYNC`.
- `fifo_setsecattr()` manually locks the real vnode because FIFOFS itself does not implement functional rw locking.

## Dependencies And Interactions

- Depends on `sys/fs/fifonode.h`, STREAMS internals, namefs for mounted pipes, `fs_subr` fallbacks, Trusted Extensions labels/zones, and vnode/VFS infrastructure.
- Closely tied to external FIFO helpers such as `fifo_stropen()`, `fifo_fastoff()`, `fifo_fastflush()`, `fifo_wakewriter()`, and `fifo_wakereader()` defined elsewhere in fifofs.
- The implementation relies on careful shared `fifolock_t` state between paired pipe endpoints.
