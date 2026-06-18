# File Research: sources/os/linux/linux-stable/fs/nfsd/auth.h

Purpose: Declares NFSD credential setup.

Key responsibilities:
- Declares `nfsd_setuser(struct svc_cred *, struct svc_export *)`.

Integration:
- Included by NFSD request/auth paths that need to install client-derived credentials.

Risks and notes:
- Minimal header; implementation details remain in `auth.c`.
