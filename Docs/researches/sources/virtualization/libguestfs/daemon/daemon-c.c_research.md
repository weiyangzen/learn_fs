# File Research: sources/virtualization/libguestfs/daemon/daemon-c.c

C/OCaml bridge helpers for the daemon.

Key points:
- `guestfs_int_daemon_exn_to_reply_with_error` maps OCaml exceptions to daemon protocol errors, including Unix errors, `Failure`, `Sys_error`, `Invalid_argument`, Augeas errors, and PCRE errors.
- Converts C `mountable_t` into OCaml `Mountable.t` representation.
- Converts C string arrays to OCaml lists.
- Converts OCaml string lists, mountables, mountable lists, and hashtable-style association lists back to C return arrays.
- Isolated from `daemon.h` so most C files do not include OCaml runtime headers.
