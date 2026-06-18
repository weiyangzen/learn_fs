# File Research: sources/os/linux/linux/fs/nfsd/auth.h

Declares NFSD authentication helper entry points.

Key behavior:
- Provides the prototype for `nfsd_setuser(struct svc_cred *cred, struct svc_export *exp)`.
- Documents that the helper sets the current process fsuid/fsgid and related credentials to represent the NFS client user.

Important interactions:
- Included by NFSD code that needs to switch request-handling credentials before VFS operations.
