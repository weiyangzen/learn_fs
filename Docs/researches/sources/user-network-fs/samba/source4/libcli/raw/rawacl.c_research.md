<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawacl.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawacl.c

Purpose: `rawacl.c` implements raw SMB1 NT transaction query and set security descriptor operations for file ACLs. It bridges `RAW_FILEINFO_SEC_DESC` and `RAW_SFILEINFO_SEC_DESC` union branches to `NT_TRANSACT_QUERY_SECURITY_DESC` and `NT_TRANSACT_SET_SECURITY_DESC`.

Important APIs, types, and functions: Public-style entry points are `smb_raw_query_secdesc_send`, `smb_raw_query_secdesc_recv`, `smb_raw_query_secdesc`, `smb_raw_set_secdesc_send`, and `smb_raw_set_secdesc`. They use `union smb_fileinfo`, `union smb_setfileinfo`, `struct smb_nttrans`, `struct security_descriptor`, NDR pull/push helpers, `smb_raw_nttrans_send`, `smb_raw_nttrans_recv`, and `smbcli_request_simple_recv`.

Control flow: Query builds an 8-byte parameter block containing file number, padding, and security info flags, asks for up to `0xFFFF` data bytes, sends an NT transaction, validates the returned 4-byte parameter length against returned data, truncates the blob to the reported descriptor size, and NDR-decodes a security descriptor. Set builds the same identifying parameter block, NDR-encodes the input descriptor into the data blob, sends an NT transaction, and the sync wrapper waits for a status-only response.

State and persistence behavior: The code does not persist state locally. It reads or modifies server-side ACL state for an already-open SMB file handle. Output descriptors are talloc-allocated under the caller's memory context. Temporary NDR contexts are freed after request construction.

Dependencies and integration points: It depends on raw NT transaction helpers and generated `ndr_security` routines. It is called directly by `rawfileinfo.c` for `RAW_FILEINFO_SEC_DESC` and by setfileinfo code for security descriptor writes. Torture ACL tests and composite ACL append paths are the main consumers.

Risks: Only SMB1 file-number handles are encoded; SMB2 security descriptor operations are handled elsewhere. Query trusts the returned descriptor length only after checking it fits inside the returned data. Set returns `NULL` if NDR push fails, so sync callers receive the generic unsuccessful status from `smbcli_request_destroy(NULL)`. Security descriptor memory ownership and exact `secinfo_flags` semantics must match callers.

Test signals: `source4/torture/raw/acls.c` and raw session/security tests exercise query/set ACL behavior. Tests should cover owner/group/DACL/SACL flag combinations, malformed or short NT transaction replies, very large descriptors, and server errors from insufficient access.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawacl.c -->
