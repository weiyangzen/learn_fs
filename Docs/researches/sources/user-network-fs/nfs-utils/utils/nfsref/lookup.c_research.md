## sources/user-network-fs/nfs-utils/utils/nfsref/lookup.c

Purpose: Implements `nfsref lookup`, reading and displaying NFS basic junction metadata from a local path.

Important APIs/types/functions: `nfsref_lookup_help`, `nfsref_lookup_display_nfs_location`, `nfsref_lookup_nfs_basic`, `nfsref_lookup_unspecified`, and `nfsref_lookup`. It converts path arrays back to POSIX paths and prints all FSL flags/classes/ranking fields.

Control flow: Public lookup dispatches by junction type. Unspecified mode probes with `nfs_is_junction`; basic mode validates, calls `nfs_get_locations`, prints every linked location, and frees the list.

State and persistence: Reads persisted junction metadata but does not mutate it.

Dependencies and integration: Relies on `junction.h`, `rpcsvc/nfs_prot.h`, and `xlog`; invoked by the `nfsref` front end.

Risks and test signals: Output is human-readable and not structured, so downstream parsing is brittle. Tests should cover non-junction paths, corrupt rootpath arrays, multiple locations, and unsupported `nfs-fedfs` type handling.
