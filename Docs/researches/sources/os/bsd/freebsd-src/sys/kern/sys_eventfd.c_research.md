# File Research: sources/os/bsd/freebsd-src/sys/kern/sys_eventfd.c

## Purpose

Implements FreeBSD's `eventfd` file type: a passable kernel file object containing a 64-bit event counter with read, write, poll, kqueue, stat, close, and kinfo support.

## Main responsibilities

- Create an eventfd-backed `struct file` via `eventfd_create_file()`.
- Provide reference management through `eventfd_get()` and `eventfd_put()`.
- Provide signaling through `eventfd_signal()`.
- Implement file operations:
  - `eventfd_read()`
  - `eventfd_write()`
  - `eventfd_ioctl()`
  - `eventfd_poll()`
  - `eventfd_kqfilter()`
  - `eventfd_stat()`
  - `eventfd_close()`
  - `eventfd_fill_kinfo()`

## Key data structures

- `struct eventfd`
  - `efd_count`: 64-bit counter.
  - `efd_flags`: creation flags such as `EFD_NONBLOCK` and `EFD_SEMAPHORE`.
  - `efd_sel`: `select`/`poll`/kqueue notification state.
  - `efd_lock`: mutex protecting state.
  - `efd_refcount`: lifetime management.
- `eventfdops`
  - File operation vector for `DTYPE_EVENTFD`.
- `eventfd_rfiltops` and `eventfd_wfiltops`
  - kqueue filters for readability and writability.

## Important control flow

- `eventfd_create_file()` allocates and initializes the object, maps nonblocking flags to file flags, and calls `finit()`.
- `eventfd_read()` blocks until count is nonzero unless nonblocking. It either returns/decrements `1` in semaphore mode or returns the full count and resets it to zero.
- `eventfd_write()` copies in a 64-bit count, rejects `UINT64_MAX`, blocks if adding would overflow the allowed counter range, and wakes waiters after adding.
- `eventfd_signal()` increments by one unless already saturated at `UINT64_MAX`, then wakes waiters.
- `eventfd_poll()` reports readable when count is nonzero and writable when count is below `UINT64_MAX - 1`.
- kqueue filters expose read data as current count and write data as remaining writable capacity.
- `eventfd_put()` drains selection state, destroys knote list and mutex, then frees when refcount reaches zero.

## Filesystem/storage relevance

This is not a filesystem implementation, but it is a special descriptor type that participates in the same descriptor, poll/select, kqueue, and process file table infrastructure as regular files. It is also exposed through `sys_generic.c` via `SPECIALFD_EVENTFD`.

## Edge cases and safeguards

- Static assertions require `EFD_CLOEXEC == O_CLOEXEC` and `EFD_NONBLOCK == O_NONBLOCK`.
- Reads/writes require at least `sizeof(eventfd_t)` bytes.
- Write of `UINT64_MAX` is invalid.
- Nonblocking write rollback restores `uio_resid` before returning `EAGAIN`.
- `FIONBIO` and `FIOASYNC` are accepted as no-op ioctls.
- `eventfd_stat()` reports FIFO-like mode.

## Research notes

Classify as kernel special-file descriptor implementation. Cross-reference with `sys_generic.c` `kern_specialfd()` and polling/select support.
