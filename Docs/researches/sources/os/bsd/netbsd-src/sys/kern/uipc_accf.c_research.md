# File Research: sources/os/bsd/netbsd-src/sys/kern/uipc_accf.c

## Purpose

`uipc_accf.c` implements the accept-filter registry and socket option support for NetBSD listen sockets. Accept filters delay completed accepts until protocol-specific readiness criteria are met.

## Main Responsibilities

- Initializes the global accept-filter list and `net.inet.accf` sysctl node.
- Registers and unregisters `struct accept_filter` implementations.
- Looks up filters by name, including module autoload attempts.
- Implements getsockopt/setsockopt support for `SO_ACCEPTFILTER`.
- Attaches filter instance state to listening sockets.
- Clears filters and releases in-flight queued sockets.

## Core Data Model

`accept_filtlsthd` is the global list of registered filters, protected by `accept_filter_lock`. Each filter has a reference count incremented on lookup and decremented when a socket filter instance is cleared or setup fails.

A listen socket's `so_accf` points to `struct so_accf`, which stores the selected filter, optional string, and filter-specific argument created by `accf_create`.

## Socket Option Behavior

`accept_filt_getopt()` requires a listening socket with an installed filter and returns `struct accept_filter_arg`.

`accept_filt_setopt()` treats a null/empty option as clear. Otherwise it copies and terminates the requested name/argument, looks up or autoloads the filter, preallocates instance storage, locks the socket, verifies it is a listen socket without an existing filter, calls `accf_create` if present, then installs `so_accf` and sets `SO_ACCEPTFILTER`.

`accept_filt_clear()` removes the filter from a listen socket, disables accept-filter upcalls on sockets still in the incomplete queue, calls `accf_destroy` if provided, frees stored state, clears `SO_ACCEPTFILTER`, and drops the filter reference.

## Concurrency Notes

The registry uses an rwlock and `RUN_ONCE` initialization. Socket operations assert or acquire the socket lock as documented: `accept_filt_clear()` expects it held, while `accept_filt_setopt()` is entered unlocked and returns with the socket locked.
