# sources/user-network-fs/samba/source3/libsmb/auth_generic.c

## Purpose
`auth_generic.c` provides convenience wrappers for setting credentials and starting client-side GENSEC authentication mechanisms for libsmb users. It assembles the source3 backend list with Kerberos, NTLMSSP, SPNEGO, SCHANNEL, and local-system options.

## Important APIs, types, and functions
- `auth_generic_set_username()`, `auth_generic_set_domain()`, and `auth_generic_set_password()` update the state's `cli_credentials`.
- `auth_generic_set_creds()` replaces the credentials object.
- `auth_generic_client_prepare()` allocates `auth_generic_state`, initializes source3 loadparm/GENSEC settings, orders the backend list, starts a GENSEC client, creates guessed credentials, and returns the state.
- `auth_generic_client_start()`, `_by_name()`, `_by_authtype()`, and `_by_sasl()` transfer credentials into GENSEC and start the selected mechanism.

## Control flow
Prepare allocates state, initializes a loadparm context, gets GENSEC settings, allocates a backend array, calls `gensec_init()`, inserts Kerberos GSE first when available, then NTLMSSP, NTLMSSP resume ccache, SPNEGO, SCHANNEL, and NCALRPC-as-system. It starts client GENSEC and guesses default credentials. Start helpers set credentials on the GENSEC context, unlink local credential ownership, null the pointer, then start a mechanism by OID, name, auth type, or SASL list.

## State and persistence behavior
State is talloc-owned and in-memory. Credentials may initially be local to `auth_generic_state`, then ownership transfers to GENSEC. `cli_credentials_guess()` reads local configuration/environment defaults but this file does not persist changes.

## Dependencies and integration points
The file depends on NTLMSSP, GENSEC, credentials, loadparm, DCERPC auth type constants, and `gse.h`. It is a frontend used by libsmb clients, LDAP/ADS auth paths, and generic authentication consumers that need mechanism negotiation without manually constructing GENSEC settings.

## Risks and edge cases
Backend priority matters: Kerberos must precede NTLMSSP for preferred domain auth. `backends` is sized for the current list; adding mechanisms requires resizing. Start helpers consume credentials, so calling multiple start variants on the same state after success will fail unless credentials are reset. `gensec_gse_security_by_oid()` may return `NULL` in unsupported builds and the backend array must tolerate that.

## Test signals
Test mechanism startup by OID/name/auth type/SASL, Kerberos-enabled and disabled builds, credential replacement before start, repeated-start failure semantics, backend priority order, SCHANNEL/NCALRPC selections, and default credential guessing from source3 config.
