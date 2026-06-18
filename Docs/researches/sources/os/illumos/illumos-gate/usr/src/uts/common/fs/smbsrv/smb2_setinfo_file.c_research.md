# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_setinfo_file.c

Implements SMB2 file information set operations.

Key behavior:
- Dispatches file set-info classes for basic info, rename, hard link, disposition, position, full EA, mode, allocation size, EOF, pipe info, valid data length, and short name.
- Restricts most operations to disk/printer handles; pipe handles only accept `FilePipeInformation`.
- Rename and link decode replace flags, root directory, and Unicode target name, reject rootdir-based relative opens, and call common setinfo helpers.
- Position updates `of->f_seek_pos` under the open-file mutex.
- Full EAs are unsupported.
- Mode currently decodes but does not store write-through/sequential/no-buffering mode.
- Valid data length frees/zeroes from EOD to EOF via `smb_fsop_freesp()`.
- Short-name changes are not allowed, even when short names are supported.

Important dependencies:
- Common setters: `smb_set_basic_info`, `smb_set_disposition_info`, `smb_set_alloc_info`, `smb_set_eof_info`, `smb_setinfo_rename`, `smb_setinfo_link`.
- Filesystem operation: `smb_fsop_freesp`.

Notable details:
- Several Windows features are accepted only enough to return compatible no-op or explicit unsupported statuses.
