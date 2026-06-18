## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_Null.c

Purpose: implements MOUNT `NULL` health/no-op procedure.

APIs and flow: `mnt_Null` logs and returns `MNT3_OK`; `mnt_Null_Free` is a no-op.

State/dependencies: no state or FSAL dependencies.

Risks/tests: minimal. Test that descriptor XDR void in/out paths dispatch and reply successfully for MOUNT v1/v3.
