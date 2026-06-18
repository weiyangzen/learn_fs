# File Research: sources/windows/reactos/drivers/filesystems/btrfs/security.c

## Scope And Purpose

`security.c` maps Unix-style Btrfs ownership metadata to Windows security descriptors and implements `IRP_MJ_QUERY_SECURITY` and `IRP_MJ_SET_SECURITY`. It also creates default security descriptors, inherits descriptors for new files, persists descriptor changes through the FCB dirty path, and derives Btrfs uid/gid values from Windows token/SID data.

Complete file read: 1012 lines.

## SID And Mapping Model

The file defines compact `sid_header` structures for common SIDs:

- BUILTIN\Administrators
- NT AUTHORITY\SYSTEM
- BUILTIN\Users
- NT AUTHORITY\Authenticated Users

`def_dacls` defines the top-level/default DACL: administrators and SYSTEM get full access, users get read/execute inheritance, authenticated users get read/write/execute/delete entries, with a FIXME for mandatory integrity labels.

External mapping state is held in `uid_map_list`, `gid_map_list`, and protected by `mapping_lock`.

`add_user_mapping` and `add_group_mapping` parse textual SID strings of the form `S-1-...`, allocate binary SID buffers, and append uid/gid mappings. They mutate the input SID string by replacing dashes with NULs while parsing.

`uid_to_sid` first checks explicit uid mappings. If none exists, uid 0 maps to SYSTEM, and other uids map to Samba-style `S-1-22-1-<uid>`.

`sid_to_uid` performs the inverse lookup: explicit mapping first, SYSTEM to uid 0, Samba `S-1-22-1-X` to `X`, otherwise `UID_NOBODY`.

`gid_to_sid` always emits Samba-style `S-1-22-2-<gid>` unless a future FIXME is implemented.

## Descriptor Creation And Loading

`load_default_acl` constructs an ACL from `def_dacls`.

`get_top_level_sd` creates an absolute security descriptor for a root/top-level FCB, sets owner from `st_uid`, group from `st_gid`, attaches the default DACL, converts it to self-relative form, and stores it in `fcb->sd`.

`fcb_get_sd` fills `fcb->sd` for an existing file:

- If requested, it first tries to load the `EA_NTACL` extended attribute.
- Without a parent, it calls `get_top_level_sd`.
- With a parent, it uses `SeAssignSecurityEx` for inherited security, converts the result to absolute form, replaces owner/group with values derived from the inode uid/gid, converts back to self-relative form, and stores the updated descriptor.

Alternate data streams use their parent file’s descriptor when queried or set.

## Query Security Dispatch

`get_file_security` calls `SeQuerySecurityDescriptorInfo` against the effective FCB security descriptor.

`drv_query_security` is the `IRP_MJ_QUERY_SECURITY` dispatch routine. It validates that the device is a filesystem VCB, checks for a CCB, enforces `READ_CONTROL` for user-mode callers, maps the caller buffer, delegates to `get_file_security`, and completes the IRP. If the descriptor does not fit, it maps `STATUS_BUFFER_TOO_SMALL` to `STATUS_BUFFER_OVERFLOW` and returns the needed length in `IoStatus.Information`.

## Set Security Dispatch

`set_file_security` applies descriptor changes:

- Rejects readonly volumes and readonly subvolumes.
- Resolves ADS operations to the parent FCB.
- Acquires the FCB resource exclusively.
- Calls `SeSetSecurityDescriptorInfo`.
- Frees the old descriptor after success.
- Updates ctime unless the user explicitly set change time.
- Updates inode transaction, sequence, root transaction/time, and dirty flags.
- Marks the FCB dirty and sends a `FILE_NOTIFY_CHANGE_SECURITY` notification.

`drv_set_security` validates the VCB/CCB, derives required access from requested security fields (`WRITE_OWNER`, `WRITE_DAC`, `ACCESS_SYSTEM_SECURITY`), enforces those rights for user-mode callers, calls `set_file_security`, and completes the IRP.

## New File Ownership And Group Selection

`search_for_gid` scans explicit gid mappings for a matching SID and writes `st_gid`.

`find_gid` chooses a new object’s gid. If the parent has `S_ISGID`, it inherits the parent gid. Otherwise it scans the caller token owner, primary group, and group list under `mapping_lock`, using the first SID found in `gid_map_list`.

`fcb_get_new_sd` creates a security descriptor for a newly created object using `SeAssignSecurityEx`, then extracts the descriptor owner and maps it back to `st_uid`; finally it calls `find_gid` to choose `st_gid`.

## Integration Points

This file connects Windows security APIs (`SeAssignSecurityEx`, `SeQuerySecurityDescriptorInfo`, `SeSetSecurityDescriptorInfo`, `Rtl*SecurityDescriptor`, token query APIs, generic file object mappings) to Btrfs inode fields (`st_uid`, `st_gid`, `st_ctime`, `st_mode`, `sequence`) and driver state (`sd_dirty`, `sd_deleted`, `inode_item_changed`, root item timestamps, dirty FCB queue, security change notification).

## Risks And Notes

- The SID string parsers modify their input buffers in place; callers must pass mutable buffers.
- `add_user_mapping` and `add_group_mapping` compute SID size from dash count. Because the authority plus subauthority parsing is hand-written, malformed SID strings may produce partially populated SID buffers rather than a clean parse failure.
- `gid_to_sid` does not consult `gid_map_list`, while `find_gid` does use it for reverse mapping from token SIDs to gids. Group SID round-tripping is therefore intentionally incomplete.
- In `fcb_get_sd`, several error paths after `SeAssignSecurityEx` can return without freeing the newly assigned `fcb->sd`; callers should treat partial descriptor setup failures carefully.
