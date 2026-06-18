# File Research: sources/os/bsd/openbsd-src/sys/sys/srp.h

Safe reference pointer and SRP list interface.

This header defines `struct srp` as a protected pointer slot, hazard/reference state, garbage-collection callbacks, and singly linked lists built from SRP pointers. On multiprocessor kernels, SRP operations use hazard protection and finalization; on uniprocessor kernels, many operations collapse to locked direct access.

The SRPL macros provide locked insertion/removal and protected traversal for singly linked lists while invoking reference callbacks and GC updates as links change. The list API is designed for readers that enter/follow/leave references safely while writers update under external locking.

Filesystem/storage relevance: generic concurrency support. VFS, device, network, or storage code can use SRP when pointer replacement and deferred destruction are needed without blocking readers.
