# File Research: sources/os/linux/linux/fs/nfsd/xdr3.h

`xdr3.h` defines NFSv3 server-side XDR argument/result structures and encoder/decoder prototypes. It builds on `xdr.h` and adds NFSv3 features: 64-bit offsets, weak cache consistency filehandles, access checks, commit, create modes/verifiers, mknod, readdirplus, filesystem info/pathconf, and POSIX ACL procedure storage.

Important argument types:
- `nfsd3_sattrargs` includes guard-time checking.
- Read/write/commit use 64-bit offsets.
- Create includes create mode and verifier pointer.
- Mknod carries file type plus major/minor.
- Readdir carries 64-bit cookie, count, and verifier.
- ACL get/set arguments include masks and POSIX ACL pointers.

Important response types:
- Attr, dirop, access, readlink, read, write, rename, link, readdir, fsstat, fsinfo, pathconf, commit, and getacl result structures.
- `nfsd3_readdirres` carries an XDR stream, dirlist buffer, scratch filehandle for readdirplus, common readdir callback state, cookie offset, and request pointer.
- `nfsd3_fhandle_pair` is a release-helper dummy wrapper for two filehandles.

`union nfsd3_xdrstore` centralizes scratch storage and `NFS3_SVC_XDRSIZE` exposes its size to the service layer.

The prototype set covers all NFSv3 procedure decoders/encoders, release callbacks, cookie/entry/readdirplus encoders, and helper functions for ACL XDR support. This header is the ABI between NFSv3 RPC procedure dispatch and the XDR encode/decode implementation.
