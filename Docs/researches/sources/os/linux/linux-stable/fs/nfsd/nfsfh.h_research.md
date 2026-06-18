# File Research: sources/os/linux/linux-stable/fs/nfsd/nfsfh.h

## Summary
Defines NFSD’s internal and wire filehandle structures plus helper APIs for filehandle manipulation.

## Contents
`struct knfsd_fh` stores raw handle bytes and current size. `struct svc_fh` wraps the raw handle with validated dentry/export references, write-mount state, WCC flags, pre/post attributes, NFSv4 change attributes, and readdir-cookie capability flags. The header defines fsid encodings, fsid-source classification, `mk_fsid()`, `key_len()`, copy/init/match helpers, write-protection helpers, and filehandle hashing.

## Important Details
Filehandle bytes begin with version, auth type, fsid type, and fileid type. Supported fsid encodings include device, explicit numeric fsid, deprecated major/minor, encoded device, UUID-derived, and UUID+inode forms. `fh_copy()` warns if the source has a validated dentry because it is intended for raw/unverified handles.

## Risks
The raw filehandle format is an ABI. Host-endian and network-endian historical encodings coexist, so changes to `mk_fsid()` or `key_len()` can break old clients or export-cache lookup. `fh_want_write()` requires paired `fh_drop_write()`, normally through `fh_put()`.
