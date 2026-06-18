# File Research: sources/os/linux/linux-stable/fs/smb/client/cifsacl.c

Read status: complete.

## Purpose

Implements CIFS/SMB security descriptor, SID, ACE, ACL, UID/GID, mode-bit, and POSIX ACL translation logic. This file is the bridge between Windows/CIFS NT security descriptors and Linux VFS ownership/permission attributes.

## Main Responsibilities

- Registers and tears down the `cifs.idmap` key type used for SID-to-id and id-to-SID request-key upcalls.
- Maps SIDs to Linux `kuid_t`/`kgid_t` values, including fast paths for well-known Unix SID forms.
- Maps Linux UID/GID values back to SIDs for chown/chgrp operations.
- Parses NT security descriptors and DACLs into `struct cifs_fattr` ownership and mode fields.
- Builds modified security descriptors for chmod/chown/chgrp and sends them back to the server.
- Converts between POSIX mode bits and CIFS ACE access masks.
- Supports special SIDs used by NFS/Apple-style SMB servers for Unix uid/gid/mode persistence.
- Provides legacy CIFS ACL get/set helpers when insecure legacy and POSIX ACL support are compiled in.

## Key Data and Constants

- Well-known SIDs:
  - `sid_everyone`
  - `sid_authusers`
  - `sid_unix_users`
  - `sid_unix_groups`
  - `sid_unix_NFS_users`
  - `sid_unix_NFS_groups`
  - `sid_unix_NFS_mode`
- `root_cred` stores a kernel credential with a private `.cifs_idmap` thread keyring for idmap upcall caching.
- SID types use `SIDOWNER` and `SIDGROUP` to distinguish owner and group mappings.

## Important Functions

- `cifs_idmap_key_instantiate()` / `cifs_idmap_key_destroy()`
  - Key payload lifetime handlers for `cifs.idmap`.
  - Small payloads are stored inline in the key payload union; larger payloads are copied with `kmemdup()`.

- `init_cifs_idmap()` / `exit_cifs_idmap()`
  - Register/unregister the `cifs.idmap` key type.
  - Allocate/revoke the private keyring used by root override credentials.

- `sid_to_key_str()`
  - Converts an SMB SID into request-key text such as owner/group SID keys.
  - Handles 48-bit SID authority formatting, including hex formatting for large authorities.

- `compare_sids()`
  - Lexicographically compares SID revision, authority bytes, and subauthorities.

- `is_well_known_sid()`
  - Recognizes `S-1-22-*` and `S-1-5-88-*` Unix SID forms.
  - Extracts Unix uid/gid directly when possible.

- `id_to_sid()`
  - Requests a SID from userspace for a Linux uid/gid using `oi:<id>` or `gi:<id>` key descriptions.
  - Validates returned SID payload length before copying.

- `sid_to_id()`
  - Maps a SID into `fattr->cf_uid` or `fattr->cf_gid`.
  - Uses direct Unix SID extraction for `idsfromsid` or SMB POSIX extensions before falling back to idmap upcall.
  - Falls back to mount uid/gid on failed mapping and returns success unless malformed SID/key data is detected.

- `validate_dacl()`
  - Bounds-checks DACL and ACE layout.
  - Rejects undersized ACLs, invalid ACE sizes, zero subauthority SIDs in ACEs, and excessive subauthority counts.

- `parse_dacl()`
  - Converts matching owner/group/everyone/authenticated-users ACEs into mode bits.
  - Supports special `S-1-5-88-3` mode SID when `mode_from_special_sid` is enabled.

- `access_flags_to_mode()` / `mode_to_access_flags()`
  - Convert between CIFS access masks and POSIX rwx bits.
  - Preserves deny/allow ordering semantics and uses `FILE_DELETE_CHILD` to approximate sticky-bit behavior.

- `populate_new_aces()`
  - Creates replacement ACEs for chmod.
  - Handles `modefromsid`, SMB POSIX mode SID behavior, deny ACEs for restrictive owner/group modes, and sticky-bit delete-child handling.

- `set_chmod_dacl()`
  - Retains unrelated ACEs, replaces owner/group/everyone/authenticated-users/mode ACEs, and preserves inherited ACE ordering.

- `build_sec_desc()`
  - Builds a new security descriptor for chmod/chown/chgrp.
  - Can synthesize owner/group SIDs from special `S-1-5-88-{1,2}` form when `idsfromsid` is active, otherwise uses idmap upcalls.

- `parse_sec_desc()`
  - Extracts owner SID, group SID, and DACL from a security descriptor and updates `struct cifs_fattr`.

- `cifs_acl_to_fattr()`
  - Public conversion path used by inode attribute code to populate mode/uid/gid from server ACLs.

- `id_mode_to_cifs_acl()`
  - Public conversion path used by chmod/chown/chgrp to retrieve an existing descriptor, build a modified one, and call dialect-specific `set_acl`.

- `cifs_get_acl()` / `cifs_set_acl()`
  - POSIX ACL xattr-style accessors for legacy CIFS POSIX support; return unsupported when not compiled in.

## Dependencies

- Uses structures from `cifsacl.h`, common SMB ACL definitions, `cifsglob.h`, `cifsproto.h`, and mount context state from `fs_context.h`.
- Calls dialect-specific operations through `server->ops->get_acl`, `get_acl_by_fid`, and `set_acl`.
- Uses request-key infrastructure, kernel credentials, POSIX ACL helpers, and Linux idmapping primitives.

## Notable Behaviors

- Malformed SID/DACL inputs are routed through `smb_EIO*()` helpers for traceable `-EIO`, or `-EINVAL` for illegal layout.
- The DACL parser does not require canonical ACE order; it tracks allow/deny effects as ACEs are encountered.
- Chmod can deliberately reduce the mode it reports back through `*pnmode` when the exact requested mode cannot be represented cleanly as NT ACEs.
- ACL read paths prefer an already open readable handle when available, avoiding path opens where possible.
