# File Research: sources/os/linux/linux/fs/nfsd/Kconfig

Defines Linux NFSD configuration options and feature dependencies.

Key behavior:
- `NFSD` enables kernel NFS server support and selects core dependencies including lockd, SUNRPC, exportfs, crypto, CRC32, fsnotify, and NFS common helpers.
- `NFSD_V2` provides deprecated NFSv2 server support.
- `NFSD_V2_ACL` and `NFSD_V3_ACL` enable Solaris NFS ACL extension support for v2/v3 as applicable.
- `NFSD_V4` enables NFSv4 server support, depends on procfs, selects POSIX ACL support, RPCSEC_GSS_KRB5, grace-period tracking, and optionally SSC helper support.
- `NFSD_PNFS` is the shared internal pNFS server switch.
- `NFSD_BLOCKLAYOUT`, `NFSD_SCSILAYOUT`, and `NFSD_FLEXFILELAYOUT` enable pNFS layout types with their block/exportfs dependencies and warnings.
- `NFSD_V4_2_INTER_SSC` enables NFSv4.2 inter-server copy support.
- `NFSD_V4_SECURITY_LABEL` enables security label attributes for NFSv4.
- `NFSD_LEGACY_CLIENT_TRACKING` retains deprecated NFSv4 stable-storage tracking methods.
- `NFSD_V4_POSIX_ACLS` enables experimental draft POSIX ACL support for NFSv4.

Important interactions:
- Controls which objects from `fs/nfsd/Makefile` and `fs/nfs_common/Makefile` are built.
- Establishes feature selection relationships between NFSD, NFS common code, pNFS layouts, ACL support, and NFSv4 recovery support.
