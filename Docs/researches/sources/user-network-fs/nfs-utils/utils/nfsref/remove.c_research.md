## sources/user-network-fs/nfs-utils/utils/nfsref/remove.c

Purpose: Implements `nfsref remove`, deleting junction metadata from a filesystem object.

Important APIs/types/functions: `nfsref_remove_help`, `nfsref_remove_nfs_basic`, `nfsref_remove_unspecified`, and `nfsref_remove`. Core metadata deletion is delegated to `nfs_delete_junction`.

Control flow: Public dispatch selects unspecified or NFS basic deletion. Basic mode treats `FEDFS_ERR_NOTJUNCT` as a failure. Unspecified mode attempts deletion and reports success even if the path was not an NFS basic junction, except for other errors.

State and persistence: Mutates local junction metadata and relies on caller `nfsref.c` to flush the exports cache on success.

Dependencies and integration: Uses `junction.h`, `xlog`, and shared type declarations.

Risks and test signals: The unspecified success path for `FEDFS_ERR_NOTJUNCT` is surprising and should be characterized. Tests should cover existing junctions, absent metadata, permission errors, unsupported type, and export-cache flush integration.
