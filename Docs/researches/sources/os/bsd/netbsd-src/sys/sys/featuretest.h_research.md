# File Research: sources/os/bsd/netbsd-src/sys/sys/featuretest.h

Read completely: 152 lines.

## Purpose
Normalizes feature-test macros so headers expose the correct standards and NetBSD extension namespaces.

## Main Interfaces
- Documents major macros: `_ANSI_SOURCE`, `_POSIX_SOURCE`, `_POSIX_C_SOURCE`, `_XOPEN_SOURCE`, `_NETBSD_SOURCE`.
- Documents minor macros: `_REENTRANT`, `_ISOC99_SOURCE`, `_ISOC11_SOURCE`, `_ISOC23_SOURCE`, `_OPENBSD_SOURCE`, `_GNU_SOURCE`.
- Converts `_POSIX_SOURCE` to `_POSIX_C_SOURCE`.
- Defaults to `_NETBSD_SOURCE` when no major macro is defined.
- Implies `_REENTRANT` for POSIX/XOPEN thread-era profiles.
- Maps `_XOPEN_SOURCE` 500/600/700/800 to corresponding `_POSIX_C_SOURCE` values.

## Dependencies And Integration
Included by many public headers such as `fcntl.h`, `event.h`, `fd_set.h`, and `float_ieee754.h`.

## Risks And Edge Cases
- Header intentionally has no include guard because behavior depends on include order and macro state.
- Visibility conditions in other headers depend on the normalized values.

## Filesystem Relevance
Moderate. Controls whether filesystem-related APIs like `openat`, `posix_fallocate`, and NetBSD flags are visible to userland.
