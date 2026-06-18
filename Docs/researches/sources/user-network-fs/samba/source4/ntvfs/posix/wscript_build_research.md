# sources/user-network-fs/samba/source4/ntvfs/posix/wscript_build

Purpose: This Waf build script declares the POSIX NTVFS backend, POSIX ACL modules, EADB helper library, and Python xattr/EADB extension modules.

Important APIs, types, and functions: It uses `bld.SAMBA_SUBSYSTEM`, `bld.SAMBA_MODULE`, `bld.SAMBA_LIBRARY`, `bld.SAMBA_PYTHON`, `bld.CONFIG_SET`, and `bld.pyembed_libname`. Targets include `pvfs_acl`, `pvfs_acl_xattr`, `pvfs_acl_nfs4`, `ntvfs_posix`, `posix_eadb`, `python_xattr_native`, `python_posix_eadb`, and `python_xattr_tdb`.

Control flow: When `WITH_NTVFS_FILESERVER` is enabled, it builds ACL backends and the internal `ntvfs_posix` module from the large set of `pvfs_*` sources plus `xattr_system.c`. Independently, it builds `posix_eadb` and the Python modules, wiring their runtime names under `samba/*.so`.

State and persistence behavior: The script itself has no runtime state. It determines whether POSIX backend code is present, whether generated prototypes are produced, and which private libraries/modules are linked into the installed Samba build.

Dependencies and integration points: Build dependencies include `NDR_XATTR`, `NDR_NFS4ACL`, `samdb`, `events`, `MESSAGING`, `LIBWBCLIENT_OLD`, `ntvfs_common`, `posix_eadb`, `tdb`, `tdb-wrap`, `attr`, Python embedding helpers, and `xattr_tdb`.

Risks: Feature gating means code can compile in one configuration but disappear in another. Missing `attr` or Python embed dependencies break the xattr modules. The long `ntvfs_posix` source list is easy to desynchronize from generated prototypes.

Test signals: Configure/build matrix tests should include `WITH_NTVFS_FILESERVER` on and off, Python enabled and disabled, native attr availability, and module load checks for `ntvfs_posix` and the three Python extension realnames.
