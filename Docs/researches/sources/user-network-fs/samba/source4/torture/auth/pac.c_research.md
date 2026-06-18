# sources/user-network-fs/samba/source4/torture/auth/pac.c

## Purpose
This torture test validates Kerberos PAC generation, decoding, checksum verification, Samba/Heimdal PAC parsing agreement, and byte-for-byte compatibility with a saved Windows Server 2003 PAC. It includes both generated self-checks and saved-blob compatibility checks.

## Important APIs, Types, And Functions
The test functions are `torture_pac_self_check`, `torture_pac_saved_check`, and suite factory `torture_pac`. It uses Kerberos keyblock helpers, `kerberos_create_pac`, `kerberos_decode_pac`, `kerberos_pac_blob_to_user_info_dc`, `kerberos_pac_logon_info`, `kerberos_encode_pac`, `make_user_info_dc_netlogon_validation`, NDR PAC parsing, SID comparison, and torture settings such as `pac_kdc_key`, `pac_member_key`, `pac_file`, `pac_client_principal`, and `pac_authtime`.

## Control Flow
The self-check initializes a Kerberos context, creates random ARCFOUR server and krbtgt keys, builds anonymous DC user info, parses a no-realm principal, creates a PAC, decodes and validates it, decodes it through Heimdal-style user-info extraction, extracts logon info, converts it back to auth user info, and compares primary SIDs. The saved check loads either the embedded `saved_pac` or an external PAC, builds configured keyblocks and principal/authtime, verifies decode and Heimdal extraction, checks expected SID for the embedded blob, re-encodes and regenerates PACs byte-for-byte when a KDC key is available, and negative-tests altered authtime and corrupted checksum.

## State And Persistence
The test uses talloc memory, Kerberos keyblock contents that must be freed, and optional file input through `pac_file`. It does not write persistent data.

## Dependencies And Integration Points
It depends on Samba Kerberos wrappers, Heimdal PAC handling, auth user-info conversion, NDR-generated PAC structures, Samba3 password hex parsing, and torture configuration. It directly exercises authentication code used by Kerberos service-ticket validation.

## Risks And Test Signals
Risks include crypto/library-version differences, embedded PAC assumptions, memory cleanup across many early failure paths, optional KDC key paths that skip encoding checks, and exact byte-for-byte comparisons that are intentionally strict. Passing tests signal PAC generation/parse compatibility, checksum enforcement, auth-time validation, SID preservation, and stable NDR layout/padding.
