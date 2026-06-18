# File Research: sources/os/linux/linux-stable/fs/nfsd/auth.c

Purpose: Applies NFS export authentication and credential squashing to NFSD worker thread credentials.

Key responsibilities:
- `nfsexp_flags` selects export flags matching the RPC credential pseudoflavor, falling back to export default flags.
- `nfsd_setuser`:
  - reverts any old override credentials,
  - prepares new credentials,
  - sets fsuid/fsgid from RPC credentials,
  - applies `all_squash` and `root_squash`,
  - remaps invalid ids to anonymous ids,
  - copies/sorts group info as needed,
  - drops or raises NFSD capability set depending on whether fsuid is root,
  - installs override credentials.

Integration:
- Used by NFSD request handling before filesystem operations.
- Depends on export flavor metadata and `svc_cred`.

Risks and notes:
- Each worker allocates its own squashed group list for root-squash handling.
- OOM during group allocation aborts prepared creds and returns `-ENOMEM`.
