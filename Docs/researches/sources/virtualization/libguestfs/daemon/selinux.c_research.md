# File Research: sources/virtualization/libguestfs/daemon/selinux.c

Optional SELinux context helpers.

Important behavior:
- Optional under `HAVE_LIBSELINUX`.
- `optgroup_selinux_available` returns true when built with libselinux.
- `optgroup_selinuxrelabel_available` historically checks `setfiles`.
- `do_setcon` calls `setcon` when available.
- `do_getcon` calls `getcon`, duplicates the returned context, then `freecon`s it.

Filesystem relevance: supports SELinux context-sensitive guest operations and relabel workflows.
