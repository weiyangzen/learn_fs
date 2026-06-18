# File Research: sources/os/linux/linux/fs/nfsd/auth.c

Implements NFSD credential override setup for servicing requests as the exported user.

Key behavior:
- `nfsexp_flags()` returns flavor-specific export flags when the request credential flavor has an override entry, otherwise falls back to the export’s default flags.
- `nfsd_setuser()` resets any old override credentials, prepares new credentials, and sets `fsuid`/`fsgid` from the RPC credential.
- Applies export squashing:
  - `NFSEXP_ALLSQUASH` maps user, group, and supplemental groups to anonymous identity.
  - `NFSEXP_ROOTSQUASH` maps root uid/gid and root supplemental groups to anonymous identity.
  - Otherwise reuses the request group list.
- Invalid uid/gid values are mapped to the export anonymous uid/gid.
- Installs supplemental groups and adjusts effective capabilities:
  - Non-root serving credentials drop the NFSD capability set.
  - Root serving credentials raise the NFSD capability set within permitted capabilities.
- Overrides current credentials with the prepared credentials.

Important interactions:
- Called by NFSD request paths before local filesystem operations.
- Enforces export-level identity mapping and capability constraints for kernel server file access.
