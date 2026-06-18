# File Research: sources/local-fs/ntfs-3g/libntfs-3g/security.c

## Scope

Implements NTFS security descriptor integration for libntfs-3g: GUID/SID formatting, `$Secure` storage and index maintenance, security-id allocation/reuse, inode descriptor retrieval/update/upgrade, Unix/POSIX ACL permission derivation, ownership/mode/ACL mutation, access checks, user/group SID mapping, NTFS file attributes, and a Win32-like security API for offline tools.

## API And Behavior

- Utility exports convert GUIDs and SIDs to text (`ntfs_guid_to_mbs()`, `ntfs_sid_to_mbs_size()`, `ntfs_sid_to_mbs()`), generate GUIDs, and compute the NTFS `$Secure` descriptor hash with `ntfs_security_hash()`.
- `$Secure` helpers model `$SII` and `$SDH` index entries, open `$Secure`, read/write `$SDS`, and add index entries. New descriptors are written twice 256 KiB apart, with optional zero stuffing to avoid `$SDS` becoming sparse.
- `setsecurityattr()` searches `$SDH` by descriptor hash, verifies full descriptor equality on hash matches, reuses existing security IDs when possible, and otherwise calls `entersecurityattr()` to allocate a new ID and append `$SDS`, `$SII`, and `$SDH` records.
- `update_secur_descr()` writes either legacy per-file `AT_SECURITY_DESCRIPTOR` attributes for NTFS 1.x style operation or NTFS 3.x `STANDARD_INFORMATION.security_id` references into `$Secure`.
- `upgrade_secur_desc()` can migrate eligible user-file legacy descriptors into `$Secure` when the add-security-IDs option is enabled.
- Descriptor retrieval uses `retrievesecurityattr()` for `$Secure:$SDS` by `$SII` security ID and `getsecurityattr()` for inode-level fallback. If no descriptor is found, a minimal administrator-owned descriptor is synthesized so later chmod/chown can create a real one.
- Group membership supports a static `/etc/group` snapshot mode and platform-specific dynamic checks via Solaris `/proc/$PID/cred` or Linux `/proc/$TID/task/$TID/status`.
- Permission caching is two-way: uid/gid/mode/POSIX ACL to security ID through generic LRU cache entries, and security ID to cached owner/group/mode/POSIX descriptor through an indexed permission table. Legacy directory descriptors without security IDs can use a separate inode-number cache.
- With `POSIXACLS`, `ntfs_get_perm()`, `ntfs_get_posix_acl()`, inheritance, creation, chmod, chown, and ACL setters operate through `POSIX_SECURITY` descriptors built by `acls.c`. Without `POSIXACLS`, the parallel paths use plain Unix mode bits.
- `ntfs_get_owner_mode()` fills stat ownership and mode fields from cache or by rebuilding permissions from NTFS descriptors, with optional legacy descriptor upgrade.
- Creation helpers allocate or inherit security IDs: `ntfs_alloc_securid()` builds descriptors from Unix/POSIX state, `ntfs_set_inherited_posix()` applies POSIX inheritance for legacy descriptors, and `ntfs_inherited_id()` builds a Windows-style inherited descriptor from the parent DACL/SACL.
- Mutation APIs include `ntfs_set_owner_mode()`, `ntfs_allowed_as_owner()`, `ntfs_set_posix_acl()`, `ntfs_remove_posix_acl()`, `ntfs_set_ntfs_acl()`, `ntfs_set_mode()`, `ntfs_set_owner()`, and `ntfs_set_ownmod()`. They enforce root/owner/group rules, clear setgid/setuid bits in selected cases, update read-only file attributes from owner write permission, and invalidate legacy caches when needed.
- Access APIs `ntfs_allowed_access()` and `ntfs_allowed_create()` implement FUSE-side permission checks, root/no-mapping shortcuts, sticky-directory handling, and setgid directory inheritance.
- Mapping setup reads an absolute mapping file with `read()` or an NTFS-resident mapping file via `ntfs_attr_data_read()`, builds user/group mappings through `acls.c`, optionally creates a default root mapping, and links static supplementary groups.
- NTFS attribute xattr helpers expose and update file attribute flags, with a restricted settable mask and directory compression propagation to `$I30` index-root flags.
- `ntfs_open_secure()`, `ntfs_close_secure()`, and `ntfs_destroy_security_context()` manage `$Secure` contexts, mappings, and caches.
- The Win32-like `SECURITY_API` layer supports offline `GetFileSecurity`/`SetFileSecurity` style descriptor selection and merging, file attribute get/set, directory enumeration, direct `$SDS/$SII/$SDH` audit reads, SID mapping queries, and root-only initialization/unmount cleanup.

## State And Dependencies

The file coordinates `ntfs_volume`, `ntfs_inode`, `STANDARD_INFORMATION`, `$Secure` streams (`$SDS`, `$SII`, `$SDH`), index contexts, `SECURITY_DESCRIPTOR_RELATIVE`, ACL/SID structures, mapping structures from `acls.c`, generic caches from `cache.c`, xattr flags, and path/inode lookup. It depends heavily on descriptor validation/building functions from `acls.c`, attribute and index mutation functions, endian helpers, inode dirty flags, mount flags, current uid/gid/tid stored in `SECURITY_CONTEXT`, and compile-time options such as `POSIXACLS`, `OWNERFROMACL`, `CACHE_LEGACY_SIZE`, and `FORCE_FORMAT_v1x`.

## Risks And Invariants

`$Secure` updates are not transactional. Comments document the intended partial-failure consequences: data-only failures are not indexed, `$SII` failures allow ID reuse later, and `$SDH` failures can leave unused `$SDS/$SII` space. Calls are expected to be serialized; the file has only a reentry guard and explicitly notes no multithread locking. Cache entries may be overwritten or relocated by later cache updates, so returned cache pointers must not be retained. Permission interpretation is intentionally approximate and may not be reciprocal between NTFS ACLs and Unix/POSIX ACLs. Descriptor validity is checked before use, but synthesized fallback descriptors can mask missing on-disk security metadata. `ntfs_guid_is_zero()` is documented as a zero-GUID check but returns the raw `memcmp()` result, so callers must be aware of the implementation behavior. Mapping failures are often treated as disabling security enforcement rather than hard mount errors.
