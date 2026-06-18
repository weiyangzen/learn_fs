# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/un.h

## Purpose
UNIX-domain socket address definition.

## Main Interfaces
- Defines `sa_family_t` when not already defined.
- Defines `struct sockaddr_un` with `sun_family` and `sun_path[108]`.
- Under extension visibility, declares `strlen` as needed and defines `SUN_LEN`.
- Kernel-only declaration includes `unp_discard`.

## Dependencies And Relationships
Used by AF_UNIX socket APIs and kernel UNIX-domain protocol code. The public version is also normally exposed through socket-related headers.

## Research Notes
The comment notes illumos does not use a BSD-style `sun_len` field, so `SUN_LEN` is based on family size plus path length.
