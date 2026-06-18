# File Research: sources/os/bsd/netbsd-src/sys/sys/pty.h

## Purpose
Declares pseudo-terminal allocation/check helpers and the `ptm_pty` handler switch used to route PTM behavior between BSD ptys and ptyfs.

## Main API
- Functions: `pty_isfree`, `pty_check`.
- PTM functions when enabled: `ptmattach`, `pty_fill_ptmget`, `pty_grant_slave`, `pty_makedev`, `pty_sethandler`, `pty_getmp`.
- Handler structure: `struct ptm_pty` with `allocvp`, `makename`, `getvattr`, `getmp`.
- Globals: optional `ptm_bsdpty`, `npty`.

## Dependencies
Uses kernel types such as `struct lwp`, `dev_t`, `struct mount`, `struct vnode`, and `struct vattr`.

## Risks and Notes
`struct mount *` arguments are meaningful for ptyfs but can be `NULL` for BSDPTY. The handler switch is a central compatibility point between old and filesystem-backed pty implementations.
