<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawfileinfo.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawfileinfo.c

Purpose: `rawfileinfo.c` implements raw SMB file and path metadata query operations. It sends SMBgetatr/getattrE and trans2 QFILEINFO/QPATHINFO requests, and parses classic, NT passthrough, Unix extension, EA, stream, security descriptor, and SMB2-style info blobs into `union smb_fileinfo`.

Important APIs, types, and functions: Major functions are `smbcli_parse_stream_info`, `smb_raw_fileinfo_passthru_parse`, `smb_raw_fileinfo_send`, `smb_raw_fileinfo_recv`, `smb_raw_fileinfo`, `smb_raw_pathinfo_send`, `smb_raw_pathinfo_recv`, and `smb_raw_pathinfo`. Local helpers include `smb_raw_info_backend`, blob send/recv wrappers, `smb_raw_getattr_send/recv`, and `smb_raw_getattrE_send/recv`.

Control flow: Send functions route non-trans2 levels to specialized SMB commands or ACL helpers, reject generic/private levels, optionally encode EA name lists, and send trans2 requests with the requested info level. Receive functions handle the special levels first, then pull a data blob and dispatch through `smb_raw_info_backend`. Passthrough parsing switches by normalized info class and validates exact or minimum blob sizes before extracting times, sizes, attributes, names, streams, EAs, file IDs, access masks, and security descriptors.

State and persistence behavior: Queries do not mutate server filesystem state. They allocate returned strings, EA arrays, stream arrays, and security descriptors under the caller's memory context. Parsing uses `req->session` for negotiated string handling and `req->transport` for DOS date conversion.

Dependencies and integration points: This file depends on trans2 helpers, ACL helpers in `rawacl.c`, EA parsers, raw string/blob helpers, GUID/security NDR parsing, and date helpers. SMB2 getinfo code reuses `smb_raw_fileinfo_passthru_parse`, so the parser supports SMB2 all-information and all-EA variants even though send paths here are SMB1.

Risks: Wire formats differ across servers; the parser accepts some documented deviations, such as 36 vs 40 bytes for basic information and the corrected all-information filename offset. `smbcli_blob_pull_string` return values are not always checked for zero, so malformed names may surface as NULL strings unless size checks catch them. Any wrong size constant or alias mapping can corrupt output silently. `req` may be NULL only on some special paths; code captures session with `req ? req->session : NULL`.

Test signals: Raw qfileinfo, streams, ACLs, Unix info2, delay-write, delete, attr, and SMB2 getinfo tests are direct signals. Tests should cover each info level, path vs handle queries, EA-list requests, stream list malformed next offsets, security descriptor parsing, non-Unicode negotiation, and server-specific short/long passthrough replies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawfileinfo.c -->
