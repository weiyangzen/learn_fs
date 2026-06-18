# sources/user-network-fs/samba/source4/auth/session.c

Purpose: converts DC-style authentication data into runtime session and security-token data, handles session transport forwarding, and lazily converts Windows claims formats.

Important APIs: `anonymous_session()`, `auth_generate_security_token()`, `auth_generate_session_info()`, transport conversion helpers, `authsam_get_session_info_principal()`, `encode_claims_set()`, and the `claims_data_*()` conversion functions.

Control flow: `auth_generate_session_info()` references account metadata from `auth_user_info_dc`, copies the session key, calls `auth_generate_security_token()`, assigns a random unique session token, and preserves ticket type. Token generation expands user/device SID lists with standard/default/authentication/NTLM/organization SIDs, then optionally expands builtin local groups from SAMDB. Transport conversion steals forwarded session info and imports/exports delegated GSS credentials when supported. Claims helpers translate between encoded PAC claim blobs, `CLAIMS_SET`, and token-ready security attributes on demand.

State/dependencies/integration: session state is in-memory and talloc-owned; claims data caches available representations with flags. It uses security token creation, DSDB nested-group expansion, Samba credentials, Kerberos/GSSAPI, generated claims NDR, and claims conversion helpers. It bridges auth subsystem results to SMB/RPC access checks and delegated credential forwarding.

Risks/test signals: SID ordering, organization SID handling, talloc reference lifetimes, and untrusted PAC claims decoding are key risks. Coverage is indirect through authentication, PAC, claims, and named-pipe forwarding tests.
