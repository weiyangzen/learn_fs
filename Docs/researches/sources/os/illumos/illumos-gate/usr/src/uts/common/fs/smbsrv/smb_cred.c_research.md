# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_cred.c

This file builds kernel credentials from authenticated SMB access tokens. It bridges SMB identity mapping, Windows SID metadata, POSIX group membership, and illumos credential structures.

Primary entry points are `smb_cred_create` and `smb_kcred_create`. Internal helpers are `smb_cred_set_sid` and `smb_cred_set_sidlist`.

`smb_cred_create` allocates a fresh cred with `crget`, preserves `PRIV_SYS_SMB` in the permitted privilege set, selects a primary gid, sets uid/gid with `crsetugid`, installs POSIX supplementary groups with `crsetgroups`, and attaches Windows SID identities for user, primary group, owner, and group list. If the SMB user maps to a non-ephemeral Unix ID and has POSIX groups, the first POSIX group is used as credential gid; otherwise the token primary group mapping is used. Failures during uid/gid or group setup free the cred and return `NULL`.

`smb_cred_set_sid` converts an SMB SID to string form, splits it into domain plus RID, copies the mapped numeric ID and SID attributes, and resolves the kernel SID domain with `ksid_lookupdomain`. The helper asserts the token identity and SID are present. `smb_cred_set_sidlist` allocates a variable-sized `ksidlist_t`, initializes each group SID through `smb_cred_set_sid`, and counts non-ephemeral IDs by comparing against `IDMAP_WK__MAX_GID`.

`smb_kcred_create` creates a blank `crget` credential for SMB-internal kcred uses such as durable-handle import, where the returned cred must later be accepted by `smb_user_setcred`.

Integration notes: this code assumes `token->tkn_posix_grps` is populated. SID-domain references obtained by `ksid_lookupdomain` become part of the cred SID structures. The normal user credential and backup/restore intent credential are separate; this file only constructs the normal token-derived cred and the minimal internal kcred variant.
