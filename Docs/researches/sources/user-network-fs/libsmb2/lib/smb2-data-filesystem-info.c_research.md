# sources/user-network-fs/libsmb2/lib/smb2-data-filesystem-info.c

## Purpose
Encodes and decodes SMB2 filesystem information classes for volume, size, device, attribute, control, full-size, object-id, and sector-size data.

## Important APIs, Types, And Functions
Exports paired codecs such as `smb2_decode_file_fs_volume_info`/`smb2_encode_file_fs_volume_info`, `smb2_decode_file_fs_size_info`/`smb2_encode_file_fs_size_info`, `smb2_decode_file_fs_device_info`/`smb2_encode_file_fs_device_info`, `smb2_decode_file_fs_attribute_info`/`smb2_encode_file_fs_attribute_info`, `smb2_decode_file_fs_control_info`/`smb2_encode_file_fs_control_info`, `smb2_decode_file_fs_full_size_info`/`smb2_encode_file_fs_full_size_info`, `smb2_decode_file_fs_object_id_info`/`smb2_encode_file_fs_object_id_info`, and `smb2_decode_file_fs_sector_size_info`/`smb2_encode_file_fs_sector_size_info`.

## Control Flow
Each decoder checks a fixed minimum length for fixed-size classes, reads little-endian fields from the iovec, and allocates decoded UTF-8 strings for variable labels or filesystem names. Encoders write fields back into an iovec and convert labels/names to UTF-16. Return values report encoded byte counts for reply construction.

## State And Persistence
Decoded variable strings are attached to the caller's memory context. The code has no global or persistent state. Encoded structs are read-only except for temporary local UTF-16 conversions.

## Dependencies And Integration Points
Used by `smb2-cmd-query-info.c` for filesystem QUERY_INFO replies. Depends on SMB2 iovec endian helpers, Windows time conversion, UTF conversion, GUID sizes, and allocation helpers.

## Risks
Volume and attribute decoders assume UTF conversion succeeds before calling `strlen`; null conversion results could crash. Variable-length decoders do not consistently verify that the declared UTF-16 name length fits inside `vec->len`. Encoders assume non-null filesystem labels/names and enough iovec space for variable data.

## Test Signals
Test every class with minimum and truncated buffers, null/empty labels, long filesystem names, UTF conversion failures, object-id exact 64-byte payloads, and sector-size flags/alignment fields.
