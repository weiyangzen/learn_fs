# File Research: sources/os/linux/linux-stable/fs/nfsd/lockd.c

## Summary
NFSD binding layer for lockd. It lets lockd open and close files through NFSD without creating a direct compile-time dependency between NFS client and server code.

## Main APIs
- `nfsd_lockd_init()` installs `nlmsvc_ops`.
- `nfsd_lockd_shutdown()` clears it.
- `nlm_fopen()` and `nlm_fclose()` implement the binding.

## Behavior
`nlm_fopen()` converts an NLM filehandle into an NFSD `svc_fh`, chooses read/write access, and calls `nfsd_open()` with NLM, owner-override, and GSS-bypass permissions. It maps `nfserr_jukebox` to `-EWOULDBLOCK`, stale filehandles to `-ESTALE`, and other failures to `-ENOLCK`.

## Risks
The GSS and NLM bypass flags are intentional compatibility behavior for older clients, but they make this path security-sensitive. `nfserr_jukebox` is used to trigger client retry rather than reporting an NLM denial.
