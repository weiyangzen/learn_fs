## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_Mnt.c

Purpose: implements MOUNT v3 `MNT`, returning an NFSv3 file handle and supported authentication flavors for an export path/tag.

APIs and flow: `mnt_Mnt` rejects unsupported MOUNT versions, normalizes a trailing slash, resolves the export by tag/pseudo/path, installs it in `op_ctx`, checks NFSv3 and access permissions, resolves the requested object through export root or `fsal_lookup_path`, converts it to an NFSv3 handle with `nfs3_FSALToFhandle`, builds auth flavor list from export security options, and returns status. `mnt3_Mnt_Free` releases allocated auth flavor array and file handle storage on success.

State/dependencies: reads export/client/security state and returns heap-owned XDR fields. Depends on FSAL lookup/root and file-handle conversion.

Risks/tests: test tag/path/pseudo resolution, access denial, auth flavor ordering, handle allocation/freeing, unsupported v1 mount, null path drop, and client UDP/TCP differences noted in comments.
