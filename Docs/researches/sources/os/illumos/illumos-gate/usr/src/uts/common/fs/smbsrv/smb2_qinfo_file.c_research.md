# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_qinfo_file.c

Implements SMB2 file information-class responses for `SMB2_0_INFO_FILE`.

Key behavior:
- `smb2_qinfo_file()` determines which underlying attributes/name/standard info are needed, gathers them, then dispatches by `qi_InfoClass`.
- Supports basic, standard, internal ID, EA size, access, name, normalized name, position, mode, alignment, all-info, alternate name, stream info, pipe info, compression info, network-open info, attribute tags, and file ID information.
- `FileAllInformation` emits the concatenated Windows layout and optionally includes file name data under `smb2_qif_all_get_name`.
- Alternate names are only returned for disk files when short-name support is enabled.
- Stream info delegates to `smb_query_stream_info()`.
- EAs are reported unsupported/no EAs.
- File ID info combines share-root fsid and target file nodeid/fsid.

Important dependencies:
- Helpers from `smb2_ofile.c`.
- Filesystem and stream helpers: `smb_query_shortname`, `smb_query_stream_info`.
- Apple behavior: `smb2_aapl_use_file_ids`, `SMB_SSN_AAPL_CCEXT`.

Notable details:
- The code intentionally mimics Windows behavior, including zeroed `FileNameInformation` inside `FileAllInformation` for newer server behavior.
- Unsupported information classes return `NT_STATUS_INVALID_INFO_CLASS`.
