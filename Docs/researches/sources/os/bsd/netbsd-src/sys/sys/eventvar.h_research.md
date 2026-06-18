# File Research: sources/os/bsd/netbsd-src/sys/sys/eventvar.h

Read completely: 71 lines.

## Purpose
Declares private kqueue implementation structures for kernel and kmem inspection.

## Main Interfaces
- Constants: `KQ_NEVENTS`, `KQ_EXTENT`, `KFILTER_MAXNAME`, `KFILTER_EXTENT`.
- `struct kqueue`: pending-event queue, mutex, owning `filedesc_t`, select info, condition variable, count/flag word.
- Count flags: `KQ_RESTART`, `KQ_CLOSING`, `KQ_MAXCOUNT`, `KQ_COUNT`.
- DDB printer: `kqueue_printit`.

## Dependencies And Integration
Includes mutex, select, and file descriptor headers. Kqueue descriptors are file objects and interact with fd table close paths and vnode knotes.

## Risks And Edge Cases
- `kq_count` combines count and state flags, so masking with `KQ_COUNT` is required.
- This is not a general public API despite being a header.

## Filesystem Relevance
Moderate. It backs file/vnode event delivery to userland.
