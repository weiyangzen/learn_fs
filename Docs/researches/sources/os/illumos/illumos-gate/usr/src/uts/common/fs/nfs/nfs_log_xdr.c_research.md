# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_log_xdr.c

## Purpose

`nfs_log_xdr.c` contains XDR encode routines for NFS server log records. It is not a full protocol XDR implementation. Instead, it serializes compact log-oriented projections of NFSv2, NFSv3, and synthetic NFSLOG operations: request metadata, credentials, remote address, export tag, filehandles, paths, names, statuses, offsets, counts, sizes, and selected result filehandles.

All routines are oriented to the kernel encode path used by `nfs_log.c`.

## Request and Buffer Headers

`xdr_nfslog_buffer_header()` encodes the log buffer header for current versions, including total header length, buffer version, 64-bit offset, flags, and timestamp. The caller initially encodes with a placeholder length, then patches the first XDR word once the final size is known.

`xdr_nfslog_request_record()` encodes the common per-request record header:

- encoded record length placeholder
- record ID
- RPC program, procedure, and version
- credential flavor
- timestamp
- real UID and GID from the kernel credential
- principal name, if present
- RPC transport netid
- export tag
- caller netbuf

It extracts principal names for AUTH_DES and RPCSEC_GSS through `nfsl_principal_name_get()`. AUTH_UNIX and AUTH_NONE do not provide a principal string.

## Synthetic NFSLOG Encoders

The synthetic logging program uses:

- `xdr_nfslog_sharefsargs()` for share/unshare records, encoding export flags, anonymous UID, path, and export filehandle.
- `xdr_nfslog_sharefsres()` for the status.
- `xdr_nfslog_getfhargs()` for privileged getfh logging, encoding the returned NFSv2-style filehandle and path.

These records let user-level log processing observe export lifecycle and getfh events even though they are not ordinary NFS protocol requests.

## NFSv2 Log Encoders

The NFSv2 routines encode only the fields relevant to logging:

- Filehandles through `xdr_fhandle()`.
- Directory operation args through `xdr_nfslog_diropargs()`.
- Attribute-setting args through `xdr_nfslog_sattr()` and `xdr_nfslog_setattrargs()`.
- Create, rename, link, symlink, read, write, readlink, readdir, and statfs args/results.
- Results usually encode status only, plus minimal successful payload such as returned filehandle, file size, byte count, EOF, or readlink text.

`xdr_nfslog_rdlnres()` copies readlink bytes into a temporary NUL-terminated string before XDR string encoding. It avoids writing raw unbounded memory but uses `KM_SLEEP`, so it can block during log encoding.

## NFSv3 Log Encoders

The NFSv3 routines follow the same compact pattern:

- `xdr_nfslog_diropargs3()` encodes directory filehandle plus name, mapping the `nfs3nametoolong` sentinel to an empty string.
- `xdr_nfslog_CREATE3args()` encodes target and creation mode, with size only for unchecked/guarded create.
- `xdr_nfslog_SETATTR3args()` encodes filehandle plus size change only.
- `xdr_nfslog_READ3args()` and `WRITE3args()` encode filehandle, offset, count, and stable mode.
- Successful read/write results encode file size, byte count, EOF, data size, or commit mode but not file data.
- Namespace operation results encode status and, on success where relevant, post-op filehandle.
- Filesystem metadata operations generally encode only status.
- `xdr_nfslog_READDIRPLUS3resok()` walks returned `dirent64` entries plus `entryplus3_info` metadata and encodes a stream of booleans, post-op filehandles, names, and final EOF.

`xdr_nfslog_nfs_fh3()` clamps malformed internal NFSv3 filehandle component lengths before delegating to `xdr_nfs_fh3_server()`. This protects logging from invalid length fields that would otherwise exceed old NFS filehandle component bounds.

## Encoding Style and Safety Properties

Most routines are small discriminated-union encoders: encode status first, then encode selected success-only payload. Failure arms usually contain no additional detail because the log record is meant for audit/transaction reconstruction, not full protocol replay.

Safety behavior includes:

- Rejecting non-encode use in key routines such as `xdr_nfslog_request_record()` and `xdr_nfslog_sharefsargs()`.
- Avoiding bulk read/write payloads.
- Mapping unsupported or invalid create modes to `FALSE`.
- Checking `READDIRPLUS` record lengths and rejecting zero-length `dirent64` records.
- Clamping invalid NFSv3 filehandle component lengths in the logging path.
- Converting non-NUL-terminated readlink data to a temporary string before XDR string encoding.

## Dependencies and Integration Points

- Called by `nfs_log.c` through logging dispatch tables.
- Uses NFS protocol types and selected ordinary XDR helpers from NFSv2/v3 XDR support, including `xdr_fhandle()`, `xdr_post_op_fh3()`, `xdr_nfs_fh3_server()`, `xdr_nfs2_timeval()`, and scalar RPC XDR helpers.
- Reads request credentials and RPCSEC_GSS raw credentials through RPC service APIs.
- Encodes export tags and metadata from `exportinfo_t`.

## Risks and Edge Cases

- `xdr_string(..., ~0)` is used for several already-kernel-resident strings. Correctness depends on those pointers being trusted and NUL-terminated.
- The file encodes a reduced semantic view. Future log consumers must not expect full NFS result details.
- `READDIRPLUS` logging assumes `objp->reply.entries`, `objp->size`, and `objp->infop` are consistent arrays produced by the server implementation.
- `xdr_nfslog_request_record()` depends on `rpc_gss_getcred()` returning usable raw credentials for RPCSEC_GSS principal extraction.
- Some routines use old-style K&R definitions, so signature mismatches are easier to miss during maintenance.

## Testing and Verification Signals

Useful tests cover every logging dispatch entry, malformed NFSv3 filehandle lengths, `nfs3nametoolong`, readlink data with embedded/nonterminated bytes, `READDIRPLUS` entries with skipped inode-zero entries, create mode variants, RPCSEC_GSS and AUTH_DES principal extraction, synthetic share/unshare/getfh records, and record-size retry behavior in `nfs_log.c`.
