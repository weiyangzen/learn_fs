# File Research: sources/os/linux/linux/fs/smb/client/cifs_unicode.h

Unicode conversion and reserved-character remapping API for CIFS.

Defines SFM private-use mappings for characters illegal or special on SMB/NTFS paths, plus remap modes `NO_MAP_UNI_RSVD`, `SFM_MAP_UNI_RSVD`, and `SFU_MAP_UNI_RSVD`.

Declares UTF-16 conversion, duplication, length, and uppercasing helpers. `cifs_remap()` derives the active remap mode from mount flags, preferring SFM mapping over SFU special-character mapping.
