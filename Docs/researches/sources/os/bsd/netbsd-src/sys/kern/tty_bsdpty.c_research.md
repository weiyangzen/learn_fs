# File Research: sources/os/bsd/netbsd-src/sys/kern/tty_bsdpty.c

## Purpose

`tty_bsdpty.c` provides the legacy BSD pty naming and vnode-allocation backend for the pty multiplexor when `COMPAT_BSDPTY` is enabled and `/dev/ptm` support is present.

## Main Responsibilities

- Defines a `struct ptm_pty` handler named `ptm_bsdpty`.
- Generates legacy `/dev/[pt]tyXX` names from pty device minors.
- Looks up the corresponding vnode with `namei`.
- Supplies default slave ownership and mode attributes.
- Reports no associated ptyfs mount for the legacy backend.

## Behavior

`pty_makename()` fills `/dev/XtyXX`, using `p` or `t` for master/slave and choosing suffix tables for old and extended minor ranges.

`pty_allocvp()` builds the legacy path and performs a `NOFOLLOW|LOCKLEAF` lookup, returning a locked vnode.

`pty_getvattr()` sets slave attributes to the caller's real UID, fixed tty group `4`, and mode `0620`.

## Integration Notes

The file is compiled only under the relevant pty options. Its exported `ptm_bsdpty` handler is installed by `ptmattach()` in `tty_ptm.c` when compatibility BSD ptys are configured.
