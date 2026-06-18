# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_aapl.c

## Purpose
SMB server-side support for Apple SMB2 `AAPL` create-context extensions and Mac-specific directory-entry metadata.

## Globals and Capabilities
- `smb2_aapl_extensions`
  - Enables/disables AAPL extension handling.
- `smb2_aapl_server_caps`
  - Currently advertises `kAAPL_SUPPORTS_READ_DIR_ATTR`.
  - `OSX_COPYFILE` and `UNIX_BASED` are intentionally disabled in comments.
- `smb2_aapl_volume_caps`
  - Advertises `kAAPL_SUPPORTS_FULL_SYNC`.
- `smb2_aapl_use_file_ids`
  - Defaults off because file IDs may not be unique under `.zfs` or submounts.
- `smb_aapl_ext_maxlen`
  - Caps response context size.

## Key Functions
- `smb2_aapl_crctx(...)`
  - Decodes AAPL create context command code.
  - Rejects when AAPL extensions are disabled.
  - Builds a response header with command code and dispatches supported commands.
  - Supports `kAAPL_SERVER_QUERY`; returns invalid info class for unsupported commands such as `kAAPL_RESOLVE_ID`.
- `smb2_aapl_srv_query(...)`
  - Decodes client bitmap and capabilities.
  - Marks the session as MacOS and AAPL-capable.
  - Intersects requested bitmap/caps with server-supported capabilities.
  - Enables `SMB_SSN_AAPL_READDIR` if read-dir attributes are negotiated.
  - Returns server and volume capabilities plus padding/null model string.
- `smb2_aapl_get_macinfo(...)`
  - Enriches directory entries for AAPL readdir.
  - Looks up the listed file to compute max access.
  - Reads `AFP_Resource` named stream size into `mi_rforksize`.
  - Reads `AFP_AfpInfo` named stream and copies Finder info bytes.
  - Optionally fills Unix mode when `kAAPL_UNIX_BASED` is enabled.

## Important Interactions
- Uses SMB server filesystem operations (`smb_fsop_lookup`, `smb_fsop_lookup_name`, `smb_fsop_read`, `smb_node_getattr`).
- AAPL state is stored in the SMB session flags and native OS marker.
- Stream names `AFP_Resource` and `AFP_AfpInfo` are queried per directory entry.

## Notes
- The code prefers normal server copy chunk behavior over Apple copyfile extensions.
- UNIX mode reporting is disabled to avoid Mac client misbehavior with nontrivial ACL-derived modes.
