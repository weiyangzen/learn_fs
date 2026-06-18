# File Research: sources/os/bsd/netbsd-src/sys/sys/file.h

Read completely: 237 lines.

## Purpose
Defines kernel file objects, file operation vectors, descriptor data unions, descriptor types, and common file I/O helpers.

## Main Interfaces
- `struct fileops`: read, write, ioctl, fcntl, poll, stat, close, kqfilter, restart, mmap, seek, advlock, pathconf, fadvise, truncate.
- `union file_data`: vnode, socket, pipe, kqueue, eventfd, timerfd, memfd, and miscellaneous backing pointers.
- `struct file`: offset, credentials, ops, data, global list, lock, flags, type, advice, reference counters.
- Descriptor types: `DTYPE_VNODE`, `SOCKET`, `PIPE`, `KQUEUE`, `MISC`, `MQUEUE`, `SEM`, `EVENTFD`, `TIMERFD`, `MEMFD`.
- Kernel helpers: `dofileread`, `dofilewrite`, vector read/write, ownership/signal helpers, common null/bad fileops, `vnops`.

## Dependencies And Integration
Includes `fcntl.h`, `unistd.h`, queue/mutex/cv headers. Vnode-backed files use `vnops`; descriptor tables in `filedesc.h` hold `struct file *`.

## Risks And Edge Cases
- `struct file` is exported by old `KERN_FILE` sysctl; fields should only be appended.
- Reference counts include normal, message-queue, and UNIX-domain deferred-close references.
- Fileops must honor offsets, credentials, locks, and descriptor flags.

## Filesystem Relevance
High. This is the core kernel abstraction for open filesystem objects.
