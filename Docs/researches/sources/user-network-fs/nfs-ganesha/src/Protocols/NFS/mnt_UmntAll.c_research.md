## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_UmntAll.c

Purpose: implements MOUNT `UMNTALL`.

APIs and flow: `mnt_UmntAll` logs and returns `NFS_REQ_OK`; `mnt_UmntAll_Free` is a no-op. It does not walk or clear any mount list.

State/dependencies: no persistent mount list state.

Risks/tests: behavior is intentionally a no-op. Test descriptor dispatch and successful void reply for MOUNT versions that include this procedure.
