<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/kerberos_pac.c -->
# sources/user-network-fs/samba/source4/auth/kerberos/kerberos_pac.c

Purpose: creates, signs, parses, and converts Kerberos PAC data between krb5 PAC buffers and Samba domain-controller auth structures. It is a security-critical bridge between Kerberos tickets and `auth_user_info_dc`.

Important APIs: `kerberos_encode_pac()` computes checksum placeholder lengths, zeroes signatures, NDR-serializes the PAC, signs the server checksum with the service key, signs that checksum with the krbtgt key for the KDC checksum, then serializes final PAC bytes. `kerberos_create_pac()` builds a four-buffer PAC containing LOGON_INFO, LOGON_NAME, SRV_CHECKSUM, and KDC_CHECKSUM from `auth_user_info_dc`. `kerberos_pac_to_user_info_dc()` parses LOGON_INFO and optional UPN_DNS_INFO, converts to `auth_user_info_dc`, optionally extracts server/KDC signatures and resource groups, and infers TGT vs non-TGT from the REQUESTER_SID buffer. `kerberos_pac_blob_to_user_info_dc()` parses a raw blob into a krb5 PAC then calls the converter.

Control flow: creation allocates a `PAC_DATA`, fills buffer descriptors, converts Samba user info to `netr_SamInfo3`, unparses the client principal without realm for LOGON_NAME, sets logon time from TGS auth time, and delegates signing. Parsing pulls krb5 buffers, uses NDR pull helpers, frees krb5-owned data promptly, calls `make_user_info_dc_pac()`, and moves the resulting structures to caller memory.

State and persistence: PAC data and parsed user info are talloc-owned; no global state. The function intentionally steals nested resource-group arrays when returning them. Ticket-type inference persists in `user_info_dc_out->ticket_type`.

Dependencies and integration: depends on Heimdal/MIT PAC APIs, Samba NDR PAC definitions, auth SAM reply conversion, credentials, Kerberos utility wrappers, and PAC checksum helpers. Used by Kerberos session-info generation and KDC ticket paths.

Risks and test signals: checksum order and key choice are security boundaries. Tests should cover missing checksum buffers, invalid NDR, absent UPN_DNS_INFO, optional resource groups, REQUESTER_SID ticket type heuristic, MIT behavior requiring allocated buffer reads, and malformed PAC blobs. Comments note deterministic NDR push assumptions for signing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/kerberos_pac.c -->
