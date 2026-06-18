# File Research: sources/os/linux/linux-stable/fs/pipe.c

## Purpose

Implements Linux anonymous pipes, FIFOs, pipe buffer lifecycle, pipe sizing/accounting, pipe poll/ioctl/fcntl behavior, and the internal `pipefs` pseudo filesystem.

## Main Responsibilities

- Provides pipe locking helpers: `pipe_lock()`, `pipe_unlock()`, and `pipe_double_lock()`.
- Implements anonymous pipe buffer operations:
  - `anon_pipe_get_page()` and `anon_pipe_put_page()` recycle temporary pages.
  - `anon_pipe_buf_release()` releases anonymous pipe pages.
  - `anon_pipe_buf_try_steal()` supports page stealing when refcount is one.
  - Generic exported helpers `generic_pipe_buf_try_steal()`, `generic_pipe_buf_get()`, and `generic_pipe_buf_release()` are used by splice/tee-style paths.
- Implements read/write paths:
  - `anon_pipe_read()` handles ordinary pipe reads, packetized buffers, whole-buffer semantics, watch queue loss notifications, blocking/nonblocking waits, and wakeups.
  - `fifo_pipe_read()` wraps reads with FIFO access-time accounting.
  - `anon_pipe_write()` handles SIGPIPE/EPIPE, page allocation, buffer merging through `PIPE_BUF_FLAG_CAN_MERGE`, packet mode via `O_DIRECT`, nonblocking behavior, and writer/reader wakeups.
  - `fifo_pipe_write()` wraps writes with timestamp update under superblock write protection.
- Implements file operations:
  - `pipe_ioctl()` supports `FIONREAD` and watch queue ioctls under `CONFIG_WATCH_QUEUE`.
  - `pipe_poll()` reports read/write readiness, EOF/HUP, and writer-side error states.
  - `pipe_release()` decrements reader/writer counts and wakes opposite endpoints.
  - `pipe_fasync()` manages async notification lists.
- Implements resource accounting:
  - Global pipe limits: `pipe_max_size`, `pipe_user_pages_hard`, `pipe_user_pages_soft`.
  - `alloc_pipe_info()` charges user pipe pages and shrinks default pipe size to `PIPE_MIN_DEF_BUFFERS` when soft-limited.
  - `free_pipe_info()` uncharges pages, releases buffers, watch queues, and cached pages.
- Implements pipe creation:
  - `get_pipe_inode()` creates pseudo inodes backed by `pipefs`.
  - `create_pipe_files()`, `__do_pipe_flags()`, `do_pipe_flags()`, and syscall wrappers `pipe()`/`pipe2()` create file pairs and install descriptors.
- Implements FIFO open semantics:
  - `fifo_open()` handles blocking/nonblocking read-only, write-only, and read-write FIFO opens, including partner wait counters.
- Implements pipe resizing:
  - `round_pipe_size()`, `pipe_resize_ring()`, `pipe_set_size()`, and `pipe_fcntl()` support `F_SETPIPE_SZ` and `F_GETPIPE_SZ`.
- Registers internal pipefs and sysctls:
  - `pipefs_init_fs_context()`, `pipe_fs_type`, and `init_pipe_fs()`.
  - Sysctls under `fs`: `pipe-max-size`, `pipe-user-pages-hard`, and `pipe-user-pages-soft`.

## Key Data/Control Flow

- Pipe ring indices use unmasked head/tail values and mask only on dereference, requiring power-of-two ring sizes.
- Read path locks `pipe->mutex`, drains buffers from tail, advances tail through `pipe_update_tail()`, and wakes writers if space was freed.
- Write path may merge a trailing partial write into the previous buffer before allocating new pages.
- Watch queue pipes cannot be written through `anon_pipe_write()` and cannot be resized through `pipe_set_size()`.
- `pipe_resize_ring()` copies existing ring contents into a new buffer array while holding `rd_wait.lock`, preserving occupancy and rejecting shrink below current occupancy.
- FIFO open uses `r_counter`/`w_counter` and `wait_for_partner()` to implement POSIX blocking partner semantics.

## Concurrency and Lifetime Notes

- `pipe->mutex` serializes most data path operations.
- Watch queue paths additionally use `pipe->rd_wait.lock` because notifications may be posted without the pipe mutex.
- `put_pipe_info()` uses `inode->i_lock` to guard `pipe->files` and clears `inode->i_pipe` on final reference.
- The file carefully wakes both wait queues when the last reader or writer disappears.

## Security/Policy Notes

- Unprivileged users are limited by pipe maximum size and per-user soft/hard page limits.
- Writes to notification/watch queue pipes return `-EXDEV`.
- `pipefs` is an internal pseudo filesystem intended not to be mounted by userspace.
