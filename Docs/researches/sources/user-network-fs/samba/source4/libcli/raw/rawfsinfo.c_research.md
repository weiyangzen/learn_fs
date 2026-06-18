<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawfsinfo.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawfsinfo.c

Purpose: `rawfsinfo.c` implements raw SMB filesystem information query and set operations. It supports the legacy `SMBdskattr` call, trans2 `TRANSACT2_QFSINFO`, passthrough filesystem info classes, and Unix CIFS setfsinfo.

Important APIs, types, and functions: Entry points are `smb_raw_fsinfo_send`, `smb_raw_fsinfo_passthru_parse`, `smb_raw_fsinfo_recv`, `smb_raw_fsinfo`, and `smb_raw_setfsinfo`. Local helpers include `smb_raw_dskattr_send/recv`, `smb_raw_qfsinfo_send`, `smb_raw_qfsinfo_blob_recv`, `smb_raw_setfsinfo_send`, and `smb_raw_setfsinfo_recv`.

Control flow: Query send dispatches `RAW_QFS_DSKATTR` to `SMBdskattr`, rejects generic levels, or sends trans2 QFSINFO with the enum value as the info level. Receive either parses the dskattr words or receives a data blob and switches by info level. Passthrough parsing extracts volume, size, device, attributes, quota, full-size, object ID, and sector-size fields with strict length checks. Setfsinfo only supports `RAW_SETFS_UNIX_INFO`, encodes version/capability into a 12-byte data blob, and sends `TRANSACT2_SETFSINFO`.

State and persistence behavior: Query paths only populate caller-provided `union smb_fsinfo` output fields. Setfsinfo can alter server-side Unix extension negotiation/capability state for the tree/session. All allocations for returned volume names, filesystem names, and GUID parsing are caller-context scoped.

Dependencies and integration points: It depends on raw trans2 helpers, `smbcli_blob_pull_string`, `smbcli_pull_nttime`, GUID NDR parsing, and the fsinfo union in `interfaces.h`. Client statfs wrappers, torture raw filesystem tests, Unix extension tests, and SMB2 filesystem info adapters use these parsers or level definitions.

Risks: The `RAW_QFS_OBJECTID_INFORMATION` switch block encloses `RAW_QFS_SECTOR_SIZE_INFORMATION` before closing the brace, making sector-size parsing visually nested and easy to modify incorrectly. The Unix info parser stores `capability` with `SVAL` even though the interface field is 64-bit, which may be intentional legacy behavior but deserves scrutiny. Strict exact-size checks may reject nonconforming servers. Generic/SMB2 handle-bearing levels are only partially represented in this SMB1 send path.

Test signals: Raw filesystem info and Unix extension torture tests should cover every query level, volume/attribute strings under Unicode and ASCII, object ID GUID parsing, quota/full-size fields, sector size info, dskattr, unsupported generic levels, and `RAW_SETFS_UNIX_INFO` status behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawfsinfo.c -->
