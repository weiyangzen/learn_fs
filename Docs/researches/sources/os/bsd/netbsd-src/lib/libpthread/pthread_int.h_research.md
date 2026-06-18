# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_int.h

This is the central private header for NetBSD libpthread internals. It defines hidden visibility, core thread structures, private attribute data, lock operation vectors, cancellation flags, magic numbers, global tuning variables, waiter structures, utility function prototypes, inline spinlock helpers, TLS-based `pthread__self`, assertion/error macros, TSD hooks, and rwlock bit layout.

`struct __pthread_st` is the key runtime thread object. It starts with `pt_self`, optional TLS pointer, magic/state/flags/cancellation word, per-thread errno, stack metadata, exit value, name, cached lock ops, start routine and argument, cleanup stack, LWP id, all-thread tree/list links, state mutex, LWP control pointer, rwlock handoff fields, sleep-object tracking, and a flexible array of per-key specific data.

The header defines cancellation bits (`PT_CANCEL_DISABLED`, `PT_CANCEL_ASYNC`, `PT_CANCEL_PENDING`, `PT_CANCEL_CANCELLED`), synchronization constants, and rwlock owner bit packing where low bits are flags and the high aligned pointer/count region stores writer owner or reader count.

Integration points: included by nearly every libpthread implementation file. ABI and memory-layout stability matter because many files assume pointer alignment, cacheline placement, and TLS access. Risks are architecture-specific TLS assumptions and the broad blast radius of changing thread or synchronization layouts.
