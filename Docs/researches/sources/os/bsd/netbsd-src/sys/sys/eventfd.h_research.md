# File Research: sources/os/bsd/netbsd-src/sys/sys/eventfd.h

Read completely: 59 lines.

## Purpose
Declares NetBSD's Linux-compatible `eventfd(2)` interface.

## Main Interfaces
- `typedef uint64_t eventfd_t`.
- Flags mapped to open flags: `EFD_SEMAPHORE`, `EFD_CLOEXEC`, `EFD_NONBLOCK`.
- Kernel entry: `do_eventfd`.
- Userland calls: `eventfd`, `eventfd_read`, `eventfd_write`.

## Dependencies And Integration
Includes `sys/fcntl.h` for flag definitions. Eventfd objects are represented as descriptor type `DTYPE_EVENTFD` in file infrastructure.

## Risks And Edge Cases
- ABI compatibility depends on preserving Linux-style flag semantics.
- `EFD_SEMAPHORE` is encoded as `O_RDWR`, so callers must treat the exported constants as ABI values, not independent bit names.

## Filesystem Relevance
Low direct relevance, but it shares file descriptor and polling/kqueue infrastructure with filesystem descriptors.
