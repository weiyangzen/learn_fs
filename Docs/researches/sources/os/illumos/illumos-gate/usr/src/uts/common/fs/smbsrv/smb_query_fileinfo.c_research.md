# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_query_fileinfo.c

## Purpose

`smb_query_fileinfo.c` implements SMB1 file and path information query commands, including Trans2 query by FID/path, legacy query information commands, passthrough NT information levels, named-pipe metadata, stream enumeration, short-name reporting, compression info stubs, and response encoding.

## Main Interfaces

- `smb_com_trans2_query_file_information()` handles Trans2 query by FID.
- `smb_com_trans2_query_path_information()` handles Trans2 query by path.
- `smb_pre_query_information()`, `smb_post_query_information()`, and `smb_com_query_information()` implement legacy path getattr.
- `smb_pre_query_information2()`, `smb_post_query_information2()`, and `smb_com_query_information2()` implement legacy FID getattr.
- `smb_query_encode_response()` encodes all supported information levels from `smb_queryinfo_t`.
- `smb_query_stream_info()` enumerates unnamed and named streams.
- `smb_query_fileinfo()` fills query data for disk files.
- `smb_query_shortname()` generates or uppercases alternate 8.3 names.

## Behavior And Data Flow

FID queries look up `sr->smb_fid`, reject invalid name-valid queries, validate pipe information levels for message pipes, then fill `smb_queryinfo_t` from either `smb_query_fileinfo()` or pipe-specific synthetic state before encoding.

Path queries reject IPC trees, reject by-path `SMB_FILE_ACCESS_INFORMATION` as unsupported, initialize and validates the path, reduce it to parent plus leaf name, look up the node, reject DFS links as `NT_STATUS_PATH_NOT_COVERED` when DFS flags apply, populate file info, reject delete-pending objects, encode the response, and release the node.

Response encoding covers legacy 16/32-bit time and size formats, EA-size placeholders, basic/standard/name/all/internal/network/open/attr-tag passthrough levels, short names, stream info, compression info with no compression, and 32-bit size saturation for older responses.

Stream enumeration follows observed Windows behavior: regular files include `::$DATA` even with no named streams; directories omit unnamed stream entries; named streams are appended from `smb_odir_read_streaminfo()` with 8-byte alignment and `NextEntryOffset` patching. Buffer exhaustion returns partial entries with `NT_STATUS_BUFFER_OVERFLOW`.

## Dependencies

This file depends on SMB path processing, SMB filesystem operations, node getattr/path helpers, short-name mangle helpers, stream directory enumeration, mbuf-chain encoding, pipe attribute helpers, and SMB status/error mapping.

## Notable Invariants And Risks

- `smb_query_by_path()` expects `sr->fid_ofile == NULL`; mixed chained commands that leave a FID set are treated cautiously as errors.
- Message pipes support only a subset of information levels and use synthetic attributes.
- Short-name queries fail with object-not-found when short names are disabled.
- Delete-on-close decrements reported link count and by-path queries return delete-pending.
- Stream enumeration treats read-stream errors as end-of-stream after already encoded entries, matching Windows-style tolerance.
- Incorrect padding or `NextEntryOffset` values in stream info can break Windows clients.
