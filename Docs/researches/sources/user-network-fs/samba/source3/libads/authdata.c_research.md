# sources/user-network-fs/samba/source3/libads/authdata.c

## Purpose
`authdata.c` obtains Kerberos tickets from username/password credentials, validates an AP-REQ through Samba GENSEC, and extracts PAC authorization data for callers.

## Important APIs and Functions
Under `HAVE_KRB5`, `spnego_gen_krb5_wrap` wraps a Kerberos ticket in a GSS/SPNEGO-style ASN.1 application token. `kerberos_return_pac` is the exported high-level API returning canonical principal/realm and a `PAC_DATA_CTR`.

## Control Flow and State
`kerberos_return_pac` creates or uses a credential cache, builds `user@realm` if needed, calls `kerberos_kinit_password_ext`, rejects the no-preauth fallback signal where expire and renew times are zero, gets a service ticket with optional S4U2SELF impersonation, wraps it as `TOK_ID_KRB_AP_REQ`, starts a server-side Kerberos GENSEC context, feeds the AP-REQ to `gensec_update`, calls `gensec_session_info`, and retrieves the PAC from the auth context. Temporary memory, ticket blobs, session keys, and in-memory ccache are cleaned up on exit.

## Dependencies and Integration Points
It depends on Kerberos helpers, PAC utilities, ASN.1 helpers, GENSEC, auth4 context, loadparm, SPNEGO constants, and Samba credential-cache helpers. It integrates with authentication paths that need to validate a password via Kerberos and derive group/PAC data without a remote SMB server.

## Risks and Test Signals
This code manipulates sensitive passwords, tickets, session keys, and PAC data; cleanup and logging must avoid leaks. Behavior depends heavily on KDC policy, PAC availability, and GENSEC backend configuration. Tests should cover cache supplied vs unique memory cache, missing PAC, expired/preauth-required accounts, wrong password, S4U2SELF failures, canonical output ownership, and request_pac toggles.
