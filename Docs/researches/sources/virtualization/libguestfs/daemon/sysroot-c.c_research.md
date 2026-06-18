# File Research: sources/virtualization/libguestfs/daemon/sysroot-c.c

## Role
Provides an OCaml binding for retrieving the daemon `sysroot` string.

## Main Operation
- `guestfs_int_daemon_get_sysroot()` returns `sysroot` as an OCaml string via `caml_copy_string`.

## Notes
This file is small glue between C daemon state and OCaml inspection code.

## Filesystem/Storage Relevance
The sysroot path is the base directory used for mounted guest filesystems inside the appliance.
