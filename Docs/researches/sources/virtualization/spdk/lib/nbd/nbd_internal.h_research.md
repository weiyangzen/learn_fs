# File Research: sources/virtualization/spdk/lib/nbd/nbd_internal.h

Internal declarations shared between NBD core and RPC code.

Key contents:
- Forward lookup and iteration helpers:
  - `nbd_disk_find_by_nbd_path`
  - `nbd_disk_first`
  - `nbd_disk_next`
- Accessors:
  - `nbd_disk_get_nbd_path`
  - `nbd_disk_get_bdev_name`
- Control helper:
  - `nbd_disconnect`

Dependencies:
- `spdk/stdinc.h` and public `spdk/nbd.h`.

Research notes:
- Keeps RPC code independent of `struct spdk_nbd_disk` internals.
- Scope relevance: small internal API for managing active NBD exports.
