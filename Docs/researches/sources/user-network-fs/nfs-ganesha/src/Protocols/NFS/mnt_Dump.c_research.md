## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_Dump.c

Purpose: implements MOUNT protocol `DUMP`.

APIs and flow: `mnt_Dump` logs the request and returns a null mount list because Ganesha does not maintain/support the historical mount list. `mnt_Dump_Free` is a no-op.

State/dependencies: no persistent mount list state is read or written. It depends only on NFS/MOUNT result structures and logging.

Risks/tests: clients expecting mount-list introspection always see empty data. Test XDR encoding of null list and compatibility with MOUNT v1/v3 descriptor tables.
