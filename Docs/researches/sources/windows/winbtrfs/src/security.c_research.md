# File Research: sources/windows/winbtrfs/src/security.c

## Purpose

`security.c` bridges Btrfs POSIX ownership metadata and Windows security descriptors. It parses configured SID-to-UID/GID mappings, synthesizes fallback SIDs, builds default ACLs, loads or inherits file security descriptors, services `IRP_MJ_QUERY_SECURITY` and `IRP_MJ_SET_SECURITY`, updates dirty inode state after security changes, and derives POSIX UID/GID values for newly created files.

## Static Security Defaults

- `sid_header` is a compact SID representation used for built-in and synthesized SIDs.
- Built-in SIDs are defined for Administrators (`BA`), Local System (`SY`), Users (`BU`), and Authenticated Users (`AU`).
- `def_dacls` defines the default DACL used for top-level security descriptors:
  - Administrators and System get full access, with inheritable variants.
  - Users get inheritable read/execute.
  - Authenticated Users get read/write/execute/delete, including an inheritable-only ACE.
  - A FIXME notes that mandatory high integrity label support is not implemented.

## SID Mapping

- `add_user_mapping()` parses strings of the form `S-1-...`, converts identifier authority and subauthorities into a heap SID, wraps it in a `uid_map`, and appends it to `uid_map_list`.
- `add_group_mapping()` performs the same parsing for `gid_map_list`.
- `uid_to_sid()` first searches configured user mappings under `mapping_lock`. If no mapping exists, UID 0 maps to Local System (`S-1-5-18`), while other UIDs map to Samba's Unix-user SID scheme `S-1-22-1-<uid>`.
- `sid_to_uid()` searches configured mappings, maps Local System back to UID 0, recognizes Samba `S-1-22-1-<uid>`, and otherwise returns `UID_NOBODY`.
- `gid_to_sid()` synthesizes Samba Unix-group SIDs as `S-1-22-2-<gid>`.

## Default and Inherited Security Descriptors

- `load_default_acl()` computes the required ACL size from `def_dacls`, allocates an ACL, emits each `ACCESS_ALLOWED_ACE`, and copies the target SID into each ACE.
- `get_top_level_sd()` creates an absolute security descriptor, sets owner from `st_uid`, sets group from `st_gid`, attaches the default DACL, converts it to self-relative form, and stores it in `fcb->sd`.
- `fcb_get_sd()` first tries to load the `EA_NTACL` extended attribute when requested. If there is no parent, it builds a top-level descriptor. Otherwise it calls `SeAssignSecurityEx()` to inherit from the parent, converts the result to absolute form, overwrites owner/group from Btrfs inode UID/GID, converts back to self-relative form, and replaces `fcb->sd`.
- `fcb_get_new_sd()` is used on file creation. It assigns security from the parent and the caller's `ACCESS_STATE`, derives `st_uid` from the resulting owner SID, and calls `find_gid()` for group selection.

## Query Security Path

- `get_file_security()` resolves alternate data streams back to the parent FCB, then calls `SeQuerySecurityDescriptorInfo()` with the requested `SECURITY_INFORMATION` flags.
- `drv_query_security()` is the `IRP_MJ_QUERY_SECURITY` dispatch routine. It enters the filesystem, validates the device and CCB, checks `READ_CONTROL` for user-mode callers, maps the user output buffer, calls `get_file_security()`, sets `IoStatus.Information`, converts `STATUS_BUFFER_TOO_SMALL` to `STATUS_BUFFER_OVERFLOW`, completes the IRP, restores top-level IRP state, and exits the filesystem.

## Set Security Path

- `set_file_security()` rejects read-only volumes, resolves ADS streams to parent FCBs, acquires the FCB resource exclusively, rejects read-only subvolumes, calls `SeSetSecurityDescriptorInfo()` to merge the requested changes into `fcb->sd`, frees the old descriptor, updates ctime/transid/sequence/root ctime, marks security and inode metadata dirty, queues a security-change notification, and releases the resource.
- `drv_set_security()` is the `IRP_MJ_SET_SECURITY` dispatch routine. It validates device and CCB state, computes required access from requested owner/group/DACL/SACL flags (`WRITE_OWNER`, `WRITE_DAC`, `ACCESS_SYSTEM_SECURITY`), checks user-mode access, calls `set_file_security()`, completes the IRP, restores top-level IRP state, and exits the filesystem.

## GID Selection

- `search_for_gid()` scans configured group mappings for a SID and updates `fcb->inode_item.st_gid` on match.
- `find_gid()` preserves a parent's GID when the parent has the setgid mode bit. Otherwise it inspects the subject token owner, primary group, and group list, using the first SID present in `gid_map_list`.

## Notable Details

- The file deliberately keeps POSIX UID/GID and Windows ACL state connected: owner/group SIDs are regenerated from inode UID/GID after inheritance, and new inode UID/GID values are derived from the assigned Windows descriptor.
- `EA_NTACL` is preferred when available, so persisted NT ACLs override synthesized or inherited descriptors.
- Alternate data stream security queries and sets are redirected to the parent file's FCB because ADS security is stored with the owning file.
- SACL handling is mostly pass-through through Windows security APIs, but top-level descriptor synthesis includes a FIXME for mandatory label support.
- Mapping parsers mutate the input SID string by replacing dashes with NUL characters while parsing, so callers must not rely on the original buffer remaining unchanged.
