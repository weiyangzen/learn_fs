# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_tmpl.c

This file implements ctfs template vnodes for `/system/contract/<type>/template`. A template vnode owns a contract template object used by the `ct_tmpl_*` user interfaces.

Key routines:
- `ctfs_create_tmplnode()` creates a GFS file vnode and initializes its `ctfs_tmn_tmpl` with the contract type’s default template constructor.
- `ctfs_tmpl_open()` only accepts `FREAD | FWRITE | FOFFMAX`; any other open mode returns `EINVAL`.
- `ctfs_tmpl_getattr()` reports a zero-length regular file with mode `0666` and filesystem mount-time timestamps.
- `ctfs_tmpl_ioctl()` dispatches `CT_TACTIVATE`, `CT_TCLEAR`, `CT_TCREATE`, `CT_TSET`, and `CT_TGET`.
- `ctfs_tmpl_inactive()` frees the held contract template and node storage.

The ioctl path copies parameters with `ctparam_copyin()`, calls `ctmpl_set()` or `ctmpl_get()`, and handles copyout for `CT_TGET`. `CT_TCREATE` creates a contract from the template and returns the new contract ID via `rvalp`.

The vnode table exposes read-write access and ioctl support while rejecting directory operations. The main risk area is memory ownership for `ct_kparam_t.ctpm_kbuf`; `CT_TSET` always frees after `ctmpl_set()`, while `CT_TGET` frees only on `ctmpl_get()` error and otherwise transfers through copyout handling.
