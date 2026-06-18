## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_Umnt.c

Purpose: implements MOUNT `UMNT`.

APIs and flow: `mnt_Umnt` logs the path argument and returns success without removing any mount-list entry because Ganesha does not maintain a mount list. Free function is a no-op.

State/dependencies: no persistent mount state exists here.

Risks/tests: clients expecting server-side mount list updates receive success but no state change. Test null/normal path logging and XDR void response behavior.
