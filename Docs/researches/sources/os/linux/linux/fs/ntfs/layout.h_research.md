# File Research: sources/os/linux/linux/fs/ntfs/layout.h

This header is the NTFS on-disk format map for the driver. It defines packed structures, magic constants, enum flags, helper macros, and static size assertions for boot sectors, MFT records, attributes, filenames, security descriptors, indexes, reparse points, EAs, quotas, and related metadata.

Major definitions:
- Boot layout: `magicNTFS`, `struct bios_parameter_block`, and `struct ntfs_boot_sector`, with a 512-byte static assertion.
- Generic protected records: magic constants for `FILE`, `INDX`, `HOLE`, `RSTR`, `RCRD`, `CHKD`, `BAAD`, and empty records; helpers like `ntfs_is_file_recordp()` and `ntfs_is_rstr_recordp()`; `struct ntfs_record` for update sequence array metadata.
- System MFT records: `FILE_MFT`, `FILE_MFTMirr`, `FILE_LogFile`, `FILE_Volume`, `FILE_AttrDef`, `FILE_root`, `FILE_Bitmap`, `FILE_Boot`, `FILE_BadClus`, `FILE_Secure`, `FILE_UpCase`, `FILE_Extend`, and `FILE_first_user`.
- MFT records: `MFT_RECORD_*` flags, MFT reference packing/unpacking macros, `struct mft_record`, and legacy `struct mft_record_old`.
- Attribute system: `AT_*` type codes, collation rules, attribute definition flags, `struct attr_def`, non-resident attribute flags, compression layout commentary, resident flags, and `struct attr_record`.
- File metadata: `FILE_ATTR_*` flags, NTFS timestamp semantics, `struct standard_information`, `struct attr_list_entry`, filename namespace constants, `MAXIMUM_FILE_NAME_LENGTH`, and `struct file_name_attr`.
- Object IDs and security: `struct guid`, `struct object_id_attr`, SID/RID constants, `struct ntfs_sid`, ACE types/flags/access masks, `struct ntfs_ace`, object ACE flags, `struct ntfs_acl`, security descriptor flags, and `struct security_descriptor_relative`.
- `$Secure` indexing: `struct sii_index_key`, `struct sdh_index_key`, and extensive notes on `$SDS`, `$SII`, and `$SDH`.
- Volume metadata: `VOLUME_*` flags and `struct volume_information`.
- Indexing: `SMALL_INDEX` / `LARGE_INDEX`, `LEAF_NODE` / `INDEX_NODE`, `struct index_header`, `struct index_root`, `struct index_block`, index entry flags, `struct index_entry_header`, and `struct index_entry`.
- Reparse and EA metadata: `struct reparse_index_key`, many `IO_REPARSE_TAG_*` constants, `struct reparse_point`, `struct ea_information`, `NEED_EA`, and `struct ea_attr`.
- Quotas: quota flag constants, `struct quota_control_entry`, predefined quota IDs, and `QUOTA_VERSION`.

Important characteristics:
- The file uses little-endian disk types throughout and marks disk structs `__packed`.
- It embeds many format constraints directly in comments: alignment, resident/non-resident rules, sorted list/index order, variable-length record termination, and Windows-version-specific fields.
- It provides no executable algorithms beyond small magic comparison helpers and MFT reference macros; its primary role is authoritative structure layout for parser and writer code.

Role in subsystem:
Every NTFS metadata reader/writer depends on this file. It is the schema foundation used by inode loading, attribute lookup, index traversal, LogFile validation, security/quota/reparse handling, and MFT record manipulation.
