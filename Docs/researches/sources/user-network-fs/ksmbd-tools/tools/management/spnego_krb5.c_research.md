# sources/user-network-fs/ksmbd-tools/tools/management/spnego_krb5.c

## Purpose

`spnego_krb5.c` provides the Kerberos mechanism implementation behind SPNEGO. It initializes a Kerberos context/keytab/credentials, validates AP_REQ tokens, extracts the client principal and session key, creates an AP_REP, and exposes separate operations for standard KRB5 and Microsoft KRB5 OIDs. The source was read as a complete 406-line file.

## Important APIs, Types, and Functions

Exported objects are `spnego_krb5_operations` and `spnego_mskrb5_operations`. Key internals are `setup_krb5`, `setup_mskrb5`, `setup_krb5_ctx`, `cleanup_krb5`, `handle_krb5_authen`, `acquire_creds_from_keytab`, `parse_service_full_name`, `get_host_name`, and compatibility shims/macros for different krb5 APIs.

## Control Flow

Setup optionally returns early when Kerberos support is disabled, otherwise initializes krb5, resolves the configured or default keytab, parses/generates the service principal, and obtains initial credentials from the keytab. Authentication creates an auth context, calls `krb5_rd_req`, retrieves the receive subkey, builds AP_REP, extracts the authenticator client without realm, copies username/session key to `auth_out`, and wraps AP_REP through the SPNEGO encoder callback.

## State and Persistence Behavior

`struct spnego_krb5_ctx` persists in `mech_ctx->private` and owns `krb5_context`, `krb5_keytab`, and `krb5_creds`. Request outputs are allocated for `user_name`, `sess_key`, and `spnego_blob`. Keytab contents are external persistent state.

## Dependencies and Integration Points

It depends on libkrb5, DNS/hostname resolution, sockets/netdb, GLib allocation, `asn1.h`, and `spnego_mech.h`. It is built only when Kerberos dependencies are present.

## Risks and Edge Cases

`parse_service_full_name` rejects host names without a dot, which can make default host resolution fragile. The setup path aborts SPNEGO initialization if credentials cannot be acquired when Kerberos support is enabled. Principal handling has compile-time branches for krb5 library variants. Session-key copying and AP_REP cleanup require exact ownership handling.

## Test Signals

Use a test realm/keytab to validate default service name, explicit `service/host@REALM`, bad keytab, disabled Kerberos, MSKRB5 and KRB5 OIDs, AP_REQ failures, and memory cleanup under repeated authentications.
