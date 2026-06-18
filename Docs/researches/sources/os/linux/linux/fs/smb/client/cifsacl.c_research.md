# File Research: sources/os/linux/linux/fs/smb/client/cifsacl.c

## Purpose
`cifsacl.c` implements CIFS/SMB ACL handling: mapping Windows SIDs to Linux ids, translating NT security descriptors/DACLs into POSIX mode bits, building updated security descriptors for chmod/chown/chgrp, retrieving and setting ACLs through SMB protocol operations, and exposing legacy POSIX ACL get/set wrappers when configured.

## Main Responsibilities
- Registers the `cifs.idmap` key type used for SID/id upcalls.
- Converts SID strings and binary SIDs to/from Linux `kuid_t`/`kgid_t`.
- Recognizes special Unix/NFS SID formats:
  - `S-1-22-1` Unix users.
  - `S-1-22-2` Unix groups.
  - `S-1-5-88-1/2/3` NFS-style uid/gid/mode SIDs.
- Parses security descriptors and DACL ACEs into `struct cifs_fattr`.
- Builds new self-relative security descriptors for permission or ownership updates.
- Provides SMB1 legacy ACL fetch/set helpers under `CONFIG_CIFS_ALLOW_INSECURE_LEGACY`.
- Provides POSIX ACL hooks under `CONFIG_CIFS_ALLOW_INSECURE_LEGACY && CONFIG_CIFS_POSIX`.

## Key Data and Constants
- Static well-known SIDs:
  - `sid_everyone`
  - `sid_authusers`
  - `sid_unix_users`
  - `sid_unix_groups`
  - `sid_unix_NFS_users`
  - `sid_unix_NFS_groups`
  - `sid_unix_NFS_mode`
- `root_cred`: kernel credentials with a private `.cifs_idmap` thread keyring for idmap request caching.
- `cifs_idmap_key_type`: custom key type named `cifs.idmap`.

## Important Functions
- `init_cifs_idmap()` / `exit_cifs_idmap()`: register/unregister idmap key type and manage the private keyring credential.
- `sid_to_key_str()`: formats a SID as `os:S-...` or `gs:S-...` key descriptions for userspace idmap upcalls.
- `compare_sids()`: compares two SMB SIDs.
- `is_well_known_sid()`: extracts uid/gid directly from special Unix/NFS SID forms.
- `id_to_sid()`: maps a Linux uid/gid to an SMB SID via keyring upcall.
- `sid_to_id()`: maps an SMB SID to Linux uid/gid, using direct special-SID decoding first when configured, then keyring upcall.
- `validate_dacl()`: validates DACL and ACE bounds before parsing.
- `parse_dacl()`: walks ACEs and updates POSIX mode bits based on owner/group/everyone/authenticated-users ACEs or special mode SID.
- `parse_sec_desc()`: parses owner SID, group SID, and optional DACL from a server security descriptor.
- `build_sec_desc()`: builds a modified security descriptor for chmod/chown/chgrp.
- `cifs_acl_to_fattr()`: retrieves a server ACL and converts it into Linux inode attributes.
- `id_mode_to_cifs_acl()`: converts Linux mode/id changes into a new CIFS ACL and sends it to the server.
- `cifs_get_acl()` / `cifs_set_acl()`: legacy POSIX ACL xattr style hooks.

## Permission Translation
- `access_flags_to_mode()` maps Windows access masks such as `GENERIC_READ`, `GENERIC_WRITE`, `GENERIC_EXECUTE`, `FILE_*_RIGHTS`, and `FILE_DELETE_CHILD` into POSIX mode bits.
- `mode_to_access_flags()` maps POSIX read/write/execute bits back to CIFS file rights.
- `populate_new_aces()` creates canonical owner/group/everyone ACEs and optional deny ACEs to preserve POSIX semantics when Windows ACL inheritance or ordering could otherwise broaden access.
- For `modefromsid` or SMB3 POSIX mode handling, `setup_special_mode_ACE()` embeds the exact mode in `S-1-5-88-3`.

## Validation and Safety Notes
- DACL parsing has explicit length checks for ACL header, ACE header, SID subauthority count, ACE size, and DACL boundary.
- SID subauthority count is capped with `SID_MAX_SUB_AUTHORITIES`.
- Malformed idmap key payloads are invalidated.
- `sid_to_id()` deliberately falls back to mount uid/gid defaults if mapping fails.
- `id_mode_to_cifs_acl()` sizes new security descriptors pessimistically for chmod/chown cases before building them.
- Sensitive key material is not handled here except idmap payloads; crypto lives in `cifsencrypt.c`.

## Dependencies
- Depends on `cifsglob.h`, `cifsacl.h`, `cifsproto.h`, `fs_context.h`, `cifs_fs_sb.h`, and common SMB ACL definitions.
- Protocol-specific ACL operations are dispatched through `server->ops->get_acl`, `get_acl_by_fid`, and `set_acl`.
