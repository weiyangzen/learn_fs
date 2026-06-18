# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_client_secinfo.c

## Purpose
NFSv4 client SECINFO and security-flavor negotiation. This file handles `NFS4ERR_WRONGSEC` by discovering server-supported security flavors and rotating the current `servinfo4_t` security data through candidate flavors until one works.

## Supported Security Flavors
`nfs4_secinfo_init()` builds a global `SECINFO4res` list of client-supported flavors:
- `AUTH_SYS`
- Kerberos RPCSEC_GSS with services none, integrity, privacy
- `AUTH_DH`
- `AUTH_NONE`

The Kerberos V5 OID is hard-coded. The file also hard-codes pseudo flavor mappings:
- krb5: `390003`
- krb5i: `390004`
- krb5p: `390005`

`nfs4_secinfo_fini()` frees the global support list.

`secinfo2nfsflavor()` maps RPCSEC_GSS mechanism/service pairs to these pseudo flavor numbers, returning zero when no known mapping exists.

## SECINFO Data Conversion
`secinfo_create()` converts wire `SECINFO4res` entries into `sv_secinfo_t` containing kernel `sec_data_t` entries:
- RPCSEC_GSS entries allocate and fill `gss_clntdata_t`, including mechanism bytes, service, qop, username `nfs`, and server instance name.
- AUTH_DH entries are included only if the server info has usable `sv_dhsec`; otherwise they are skipped.
- AUTH_SYS/AUTH_NONE and other simple flavors become direct `sec_data_t` entries.

`secinfo_free()` frees `sv_secinfo_t`, purges cached RPCSEC_GSS auth handles with `rpc_gss_secpurge()`, releases GSS mechanism storage, and avoids freeing shared AUTH_DH data.

## Current Security Selection
`secinfo_update()` replaces `svp->sv_secinfo`, frees the prior list unless saved for recovery, resets the index, sets `SV4_TRYSECINFO`, and points `sv_currsec` at the first candidate. If no usable security info remains, it clears trial state and current security.

`secinfo_check()` advances the current index. If another flavor exists, it sets `SV4_TRYSECINFO` and updates `sv_currsec`; otherwise it resets the index and clears trial state.

`save_mnt_secinfo()` saves the mount’s original current security choice before operations that may cross mount/security boundaries.

`check_mnt_secinfo()` restores saved security when operating on a stub vnode or mount root context, and frees stale saved lists otherwise.

## Root Security Negotiation
`secinfo_tryroot_otw()` uses the global client-supported SECINFO list and tries `PUTROOTFH` with each flavor. On `NFS4ERR_WRONGSEC`, it advances to the next flavor. Other recovery-worthy errors are returned as success to let the caller retry through normal recovery. Successful completion leaves `sv_currsec` set to the flavor that worked.

## Path-Based SECINFO
`comp_total()` counts pathname components, ignoring redundant slashes. `comp_getn()` extracts the nth path component and splits a mutable path buffer so the parent path can be used for LOOKUPs.

`nfs4secinfo_otw()` performs:
`{ PUTROOTFH, LOOKUP parent components..., SECINFO target-component }`

It handles `WRONGSEC` at multiple points:
- If `PUTROOTFH` fails, it negotiates root security through `secinfo_tryroot_otw()`.
- If a LOOKUP fails with `WRONGSEC`, it backs up to the failing component, gets SECINFO for that component, updates current security, then retries the full target.
- If non-WRONGSEC recovery is needed and the caller is already the recovery thread, it schedules recovery and returns to the outer recovery loop; otherwise it returns an error.

On successful SECINFO, it updates `mi_curr_serv` security and rejects empty/unsupported server flavor lists with `EACCES`.

`nfs4_secinfo_path()` decides whether a mounted path needs SECINFO. For server root, SECINFO cannot name a component, so it uses the client-supported flavor list and tries candidates. For non-root paths it calls `nfs4secinfo_otw()`. On error, it clears current/saved secinfo state.

## Filehandle/Vnode SECINFO
`nfs4_secinfo_fh_otw()` sends `{ CPUTFH, CSECINFO }` for a parent filehandle and component name, then updates server security from the SECINFO result.

`nfs4_secinfo_vnode_otw()` wraps the filehandle SECINFO path for lookup-triggered `WRONGSEC`.

`nfs4_secinfo_vnode()` is recovery-oriented: if the vnode has a parent filehandle/name, use filehandle SECINFO; otherwise fall back to mount path SECINFO.

## Recovery Entry Point
`nfs4_secinfo_recov()` is called when the client receives `NFS4ERR_WRONGSEC`. If the mount used an explicit preferred flavor, it does not negotiate and returns the WRONGSEC errno. Otherwise it tries SECINFO with current credentials and, when configured with a non-root security uid, with a duplicated credential using that uid. It clears `MI4R_NEED_SECINFO` before returning.

## Important Invariants
- `svp->sv_lock` protects `sv_secinfo`, `sv_currsec`, `sv_save_secinfo`, and security trial flags.
- SECINFO lists may be temporarily saved across recovery and must not be freed while saved.
- Empty server SECINFO results or client-incompatible AUTH_DH-only results become `EACCES`.
- Root path security negotiation cannot use SECINFO directly because SECINFO requires a component name.
