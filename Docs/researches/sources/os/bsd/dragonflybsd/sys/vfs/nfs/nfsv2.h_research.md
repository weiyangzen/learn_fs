# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsv2.h

This is a compatibility shim for older NFS code. Its only operational content is inclusion of `nfsproto.h`, after the historical Berkeley/FreeBSD/DragonFly license and version comments.

The file carries no local constants, structures, or functions. Its role is to preserve the legacy `nfsv2.h` include path while moving actual NFS protocol definitions into `nfsproto.h`.

Dependencies: `nfsproto.h`.

Research notes: any semantic analysis for NFSv2 protocol constants should follow `nfsproto.h`; this file itself is only an include wrapper.
