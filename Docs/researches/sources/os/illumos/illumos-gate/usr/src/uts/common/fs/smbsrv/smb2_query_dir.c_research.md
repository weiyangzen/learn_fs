# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_query_dir.c

Implements SMB2 directory enumeration.

Key behavior:
- Decodes query directory requests, optional Unicode pattern, file index, flags, FID, and max output size.
- Supports standard directory formats: directory, full directory, both directory, names, file-id-both, and file-id-full.
- Uses a private pseudo information class for Apple AAPL readdir extensions when enabled.
- Opens or reuses an `smb_odir_t`, handles reopen/restart/index/continuation positioning, and tracks seek position.
- Limits output by `smb2_max_trans`, estimated entry count, `smb2_find_max`, and single-entry requests.
- Reads entries with `smb_odir_read_fileinfo()`, encodes them, and rewinds enumeration if a read entry cannot fit into the output buffer.
- Patches the final `NextEntryOffset` to zero.

Important dependencies:
- Directory abstraction: `smb_odir_openfh`, `smb_odir_reopen`, `smb_odir_resume_at`, `smb_odir_read_fileinfo`.
- Apple extension helpers: `smb2_aapl_get_macinfo`, session AAPL flags.
- Name/shortname encoding via SMB message buffers.

Notable details:
- `SMB2_QDIR_FLAG_SINGLE` maps end-of-search to `NT_STATUS_NO_SUCH_FILE`.
- Apple compact file IDs can be zeroed depending on `smb2_aapl_use_file_ids`.
