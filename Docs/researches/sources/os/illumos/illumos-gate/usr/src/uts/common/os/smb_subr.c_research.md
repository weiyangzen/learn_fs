# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/smb_subr.c

Provides small kernel support shims for SMBIOS library code, not SMB filesystem protocol code.

Functions:
- `smb_strerror()` is a stub that currently returns `NULL`.
- `smb_alloc()` wraps `kmem_alloc()` and returns `NULL` for zero-length requests.
- `smb_zalloc()` wraps `kmem_zalloc()` and returns `NULL` for zero-length requests.
- `smb_free()` wraps `kmem_free()`.
- `smb_dprintf()` prints debug output through `vcmn_err(CE_CONT, ...)` only when `SMB_FL_DEBUG` is set on the SMBIOS handle.

Filesystem relevance:
- No direct filesystem behavior. The `smb_` prefix here means SMBIOS, not Server Message Block. It is kernel utility glue for resident SMBIOS parsing/debug code.
