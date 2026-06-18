# File Research: sources/os/linux/linux/fs/nfsd/lockd.c

Read completely: 110 lines.

Binding layer between NFSD and lockd/NLM so lockd can open and close files through nfsd without requiring the NFS client module.

Key responsibilities:
- Implements `nlm_fopen`, translating an NFS filehandle into `svc_fh`, choosing read or write access from POSIX open flags, and calling `nfsd_open`.
- Adds NLM-specific access flags: bypass GSS, owner override, and `NFSD_MAY_NLM` so `insecure_locks` can bypass authentication.
- Maps nfsd status values to lockd-facing errno values, notably `nfserr_jukebox` to `-EWOULDBLOCK`, stale to `-ESTALE`, and other failures to `-ENOLCK`.
- Implements `nlm_fclose` with `fput`.
- Registers/unregisters the `nlmsvc_binding` via `nfsd_lockd_init` and `nfsd_lockd_shutdown`.

Notable risks:
- Comments document subtle client behavior around delegation conflicts and NLM denied semantics.
- NLM auth bypass is intentional but must remain limited to exports that permit it.
