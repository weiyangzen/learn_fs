# File Research: sources/os/linux/linux-stable/fs/smb/client/Makefile

## Purpose

Kbuild file for the CIFS/SMB2/SMB3 VFS client module, defining core object composition, optional feature objects, generated error-mapping tables, ASN.1 generated dependencies, and SMB KUnit test objects.

## Main Contents

- Adds `-I$(src)` to `ccflags-y` for trace-event include resolution.
- Builds `cifs.o` when `CONFIG_CIFS` is enabled.
- Core `cifs-y` includes VFS, connection, directory, file, inode, transport, Unicode, cached-dir, SMB2, ACL, fs-context, DNS, SPNEGO NegTokenInit ASN.1, namespace, and reparse support objects.
- Generated ASN.1 dependencies:
  - `asn1.o` depends on `cifs_spnego_negtokeninit.asn1.h`.
  - The generated ASN.1 object depends on generated C and header files.
- Optional objects:
  - `xattr.o` for `CONFIG_CIFS_XATTR`.
  - `cifs_spnego.o` for `CONFIG_CIFS_UPCALL`.
  - `dfs_cache.o` and `dfs.o` for `CONFIG_CIFS_DFS_UPCALL`.
  - `netlink.o` and `cifs_swn.o` for `CONFIG_CIFS_SWN_UPCALL`.
  - `fscache.o`, `smbdirect.o`, `cifsroot.o`, compression objects, and legacy SMB1 objects under their matching options.
- Generates SMB1 mapping tables from `nterr.h` and `smberr.h` using `gen_smb1_mapping` when legacy support is configured.
- Generates SMB2 mapping table from `../common/smb2status.h` using `gen_smb2_mapping`.
- Builds SMB1 and SMB2 map-error KUnit test objects under test config symbols.

## Integration Notes

- `targets` includes generated mapping tables so Kbuild tracks and cleans them.
- The file is the practical map from Kconfig feature selection to CIFS client code presence.
