# File Research: sources/os/linux/linux/fs/smb/client/Kconfig

Configuration surface for the CIFS/SMB2/SMB3 kernel client.

`CONFIG_CIFS` is the main tristate and selects networking, NLS, crypto primitives, keys, DNS resolver, ASN.1/OID support, and netfs support. Its help text positions SMB3.1.1 as the preferred modern dialect while retaining older CIFS/SMB support.

Feature toggles cover extended stats, insecure legacy dialects, SPNEGO upcalls, xattrs, CIFS POSIX extensions, debug levels, unsafe key dumping, DFS upcalls, SWN witness upcalls, broken NFSD export support, SMB Direct/RDMA, fscache, SMB rootfs, compression, and SMB1 KUnit tests.

Important dependency constraints include `CIFS_POSIX` requiring insecure legacy and xattrs, `CIFS_SMB_DIRECT` requiring InfiniBand address translation and compatible built-in/module combinations, and `CIFS_FSCACHE` matching CIFS/FSCACHE linkage.
