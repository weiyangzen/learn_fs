# File Research: sources/teaching/minix/minix/servers/vfs/request.c

Implements typed wrapper functions for VFS-to-filesystem server requests. Each wrapper builds a message, creates grants where needed, sends it through `fs_sendrec`, revokes grants, and copies reply data into VFS structures.

Major request families:
- Data I/O: `req_readwrite`, `req_breadwrite`, `req_peek`, `req_bpeek`.
- Metadata: `req_chmod`, `req_chown`, `req_utime`, `req_stat`, `req_statvfs`.
- Namespace: `req_lookup`, `req_create`, `req_mkdir`, `req_mknod`, `req_link`, `req_rename`, `req_rmdir`, `req_unlink`, `req_slink`, `req_rdlink`.
- Mount/lifecycle: `req_readsuper`, `req_mountpoint`, `req_unmount`, `req_newdriver`, `req_flush`, `req_sync`, `req_putnode`, `req_newnode`, `req_inhibread`, `req_ftrunc`.

Important behavior:
- User-buffer operations use magic grants and retry on `GRANT_FAULTED` by asking VM to handle memory with `vm_vfs_procctl_handlemem`, then repeating without `CPF_TRY`.
- VFS-local buffers use direct grants.
- `req_lookup` can pass supplemental group credentials through an extra grant when `fp_ngroups > 0`, and interprets `OK`, `EENTERMOUNT`, `ELEAVEMOUNT`, and `ESYMLINK` response shapes.
- `req_readsuper`, `req_create`, `req_newnode`, and `req_lookup` populate `node_details_t` or `lookup_res_t`.
- Some operations enforce non-`RES_64BIT` filesystem limits before sending requests.

Notable caveats:
- `req_getdents_actual` and `req_readwrite_actual` create grants before checking some 64-bit offset limits, and their early `EINVAL` paths return without revoking those grants.
- Many wrappers panic on grant allocation failure, treating grant creation failure as an internal VFS invariant violation.
