# File Research: sources/local-fs/ntfs-3g/ntfsprogs/sd.c

## Purpose
Constructs default NTFS security descriptors for formatted volumes and system files. This is builder code for fixed Windows-like descriptor layouts, not a parser.

## Public Functions
- `init_system_file_sd(int sys_file_no, u8 **sd_val, int *sd_val_len)`
- `init_root_sd(u8 **sd_val, int *sd_val_len)`
- `init_secure_sds(char *sd_val)`

## `init_system_file_sd`
- Returns a pointer to static memory containing a relative security descriptor for NTFS system files.
- Negative system file number returns `NULL` and length `0`.
- All system files except root are covered here.
- Descriptor layout:
  - Owner: Local System SID.
  - Group: Builtin Administrators SID.
  - DACL with two allow ACEs:
    - Local System.
    - Builtin Administrators.
- `$AttrDef` and `$Boot` get read-oriented masks; other system files get broader write-capable masks.
- Returned storage is static and only valid until the next call.

## `init_root_sd`
- Builds a large static descriptor matching Windows Vista-style root directory security from Disk Management formatting.
- Descriptor has owner/group Local System and an 8-ACE DACL.
- Covers:
  - Builtin Administrators direct access and inherit-only generic all.
  - Local System direct access and inherit-only generic all.
  - Authenticated Users direct access and inherited generic read/write/execute/delete.
  - Builtin Users direct read/traverse and inherited generic read/execute.
- Uses explicit offsets and little-endian conversions to create the exact self-relative descriptor image.

## `init_secure_sds`
- Fills caller-provided `$Secure:$SDS` data with two security descriptor entries matching a newly formatted Windows 2003-style partition.
- Writes `SECURITY_DESCRIPTOR_HEADER` values including hash, security ID, stream offset, and length.
- Descriptor `#1` at offset `0x00`, security ID `0x0100`, mask `0x120089`.
- Descriptor `#2` at offset `0x80`, security ID `0x0101`, mask `0x12019F`.
- Both descriptors use Local System and Builtin Administrators ACEs and Builtin Administrators owner/group SIDs.

## Dependencies
- Uses NTFS layout types and constants from `layout.h`.
- Uses endian conversion helpers/macros from the broader NTFS-3G codebase through included headers.

## Notes
- The code relies on hard-coded offsets and sizes; changes to NTFS structure definitions would require careful binary layout verification.
- `init_root_sd()` uses a 0x1000-byte ACL size inside a 0x102c-byte descriptor, leaving substantial reserved/padded space consistent with the intended Windows-created layout.
