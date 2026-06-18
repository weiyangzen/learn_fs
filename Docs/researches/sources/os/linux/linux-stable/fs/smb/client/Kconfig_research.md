# File Research: sources/os/linux/linux-stable/fs/smb/client/Kconfig

## Purpose

Defines kernel configuration for the CIFS/SMB2/SMB3 client filesystem, including core dependencies, security options, debug facilities, DFS/SWN upcalls, RDMA, FS-Cache, root filesystem support, compression, and SMB1-specific KUnit tests.

## Main Options

- `CIFS`
  - Tristate SMB3/CIFS network filesystem client.
  - Depends on `INET`.
  - Selects NLS, UCS2 utilities, crypto primitives, keys, DNS resolver, ASN.1/OID support, and netfs support.
- `CIFS_STATS2`
  - Enables extended timing/statistics for debug and slow-response reporting.
- `CIFS_ALLOW_INSECURE_LEGACY`
  - Allows legacy SMB1/CIFS and SMB2.0 dialect use.
- `CIFS_UPCALL`
  - Enables Kerberos/SPNEGO request-key upcall support.
- `CIFS_XATTR`
  - Enables CIFS extended attribute support.
- `CIFS_POSIX`
  - Enables old CIFS POSIX extensions and POSIX ACL support for legacy CIFS when xattrs and insecure legacy support are enabled.
- `CIFS_DEBUG`, `CIFS_DEBUG2`, `CIFS_DEBUG_DUMP_KEYS`
  - Enable baseline debug, extra debug, and unsafe key dumping support.
- `CIFS_DFS_UPCALL`
  - Enables DFS namespace support and userspace resolution upcalls.
- `CIFS_SWN_UPCALL`
  - Enables Service Witness Protocol userspace daemon integration.
- `CIFS_NFSD_EXPORT`
  - Broken option for exporting CIFS mounts through nfsd.
- `CIFS_SMB_DIRECT`
  - Enables SMB Direct/RDMA support and selects `SMBDIRECT`.
- `CIFS_FSCACHE`
  - Enables local FS-Cache support when CIFS and FSCACHE linkage is compatible.
- `CIFS_ROOT`
  - Enables experimental SMB root filesystem support.
- `CIFS_COMPRESSION`
  - Enables SMB 3.1.1 compression support.
- `SMB1_KUNIT_TESTS`
  - Enables SMB1-specific KUnit tests when shared SMB tests and insecure legacy support are enabled.

## Integration Notes

- Most optional symbols directly control object inclusion in `fs/smb/client/Makefile`.
- Several options have security-sensitive defaults or warnings: insecure legacy support defaults to yes, key dumping defaults to no, POSIX legacy defaults to no, compression defaults to no.
