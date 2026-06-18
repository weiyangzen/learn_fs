# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_subr.c

## Purpose
Core SMBFS client helper routines for wire/path marshalling and decoding SMB directory, file, and filesystem attribute responses.

## Main Responsibilities
- Builds full remote SMB paths from cached `smbnode::n_rpath` values.
- Converts Unicode directory names to local UTF-8 form.
- Decodes directory enumeration records for normal directory listings and named-stream listings.
- Decodes `FileAllInformation` and `FileFsAttributeInformation` responses into SMBFS internal attributes.

## Key Functions
- `smbfs_fullpath(...)`
  - Marshals the directory path plus optional child name into an `mbchain`.
  - SMB2 paths omit the leading backslash.
  - SMB1 Unicode paths may need an alignment pad and are null terminated.
  - At share root, avoids adding a duplicate separator.
  - For XATTR fake directories (`N_XATTR`), suppresses the separator so named streams use the existing colon convention.
- `smbfs_fname_tolocal(...)`
  - Converts UCS-2 little-endian names in `smbfs_fctx` to UTF-8 using `uconv_u16tou8`.
  - On conversion failure, replaces the name with `"?"` because callers do not handle conversion errors.
- `smbfs_decode_dirent(...)`
  - Decodes one directory entry from `ctx->f_mdchain`.
  - Uses `NextEntryOffset` to isolate one entry safely instead of hand-adding structure sizes.
  - Supports `FileFullDirectoryInformation`, `SMB_FIND_FULL_DIRECTORY_INFO`, and `FileStreamInformation`.
  - For stream information, skips the leading colon in stream names when present.
  - Populates `ctx->f_attr`, `ctx->f_name`, `ctx->f_nmlen`, `ctx->f_rkey`, and advances `ctx->f_eofs`.
- `smbfs_decode_file_all_info(...)`
  - Decodes the `FileBasicInformation` and `FileStandardInformation` portions of `FileAllInformation`.
  - Sets create/access/modify/change times, DOS attributes, allocation size, and file size.
- `smbfs_decode_fs_attr_info(...)`
  - Decodes filesystem capability flags, maximum component length, and filesystem type name.
  - Converts the filesystem name from UCS-2 when the VC uses Unicode strings.

## Important Interactions
- Relies on `netsmb` mchain helpers (`mb_put_*`, `md_get_*`, `smb_put_dmem`, `smb_get_dstring`).
- Path logic must stay consistent with `smbfs_getino` and `smbfs_node_findcreate` identity rules.
- XATTR path behavior is coordinated with `smbfs_xattr.c`.

## Notes
- The file deliberately keeps every node’s full remote path instead of walking parent links.
- Directory-entry parsing is defensive around short buffers and treats failures as exhaustion of the current response.
