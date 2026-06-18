# sources/user-network-fs/samba/source4/ntvfs/wscript_build

Purpose: This parent Waf script builds the NTVFS core library and recurses into backend/module subdirectories.

Important APIs, types, and functions: It declares private library `ntvfs`, recurses into `posix`, `common`, `unixuid`, and `sysdep`, and declares modules `ntvfs_cifs`, `ntvfs_simple`, and `ntvfs_ipc`.

Control flow: The core `ntvfs` library is enabled only with `WITH_NTVFS_FILESERVER`. The POSIX directory is always recursed, but most POSIX targets are internally gated. When file server support is enabled, common/unixuid/sysdep are recursed and CIFS/simple/IPC modules are built.

State and persistence behavior: The script has no runtime state, but build gating controls the installed module set and therefore available server backend behavior.

Dependencies and integration points: The core library depends on tevent and Samba module support. CIFS depends on raw SMB client libraries, simple depends on talloc, and IPC depends on named-pipe auth, GSSAPI, credentials, and DCERPC share code.

Risks: Inconsistent gating can build submodules without core support or omit required generated prototypes. The simple backend is built from only `vfs_simple.c` and `svfs_util.c`, matching its intentionally limited behavior.

Test signals: Build matrix tests should cover file server on/off and check that registered NTVFS modules match configured targets.
