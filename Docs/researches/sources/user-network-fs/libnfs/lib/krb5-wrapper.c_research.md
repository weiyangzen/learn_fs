# sources/user-network-fs/libnfs/lib/krb5-wrapper.c

## Purpose
Optional Kerberos/GSSAPI wrapper for libnfs RPCSEC_GSS authentication. It imports names, acquires credentials, initiates security contexts, exposes output tokens, and formats GSS errors.

## Important APIs, Types, And Functions
- `krb5_auth_init` creates `private_auth_data` for `nfs@server`, imports target/user names, selects SPNEGO/Kerberos mechanisms, acquires initiator credentials, and optionally constrains negotiated mechanisms.
- `krb5_auth_request` advances `gss_init_sec_context` using an optional server token and stores output tokens.
- `krb5_free_auth_data` releases GSS context, credentials, buffers, names, server string, and auth object.
- `krb5_set_gss_error` and `display_status` convert major/minor GSS codes into libnfs error strings.
- Token accessors return output token buffer and length.

## Control Flow
Initialization allocates auth data, builds the hostbased service name, imports target and user names, selects mechanism OIDs, acquires credentials, applies requested mechanism restrictions for non-Apple builds, and returns initialized state. Each request releases the previous output token, wraps input if provided, sets mutual/integrity/confidentiality flags based on requested security, calls `gss_init_sec_context`, stores the context in `rpc->gss_context`, and reports continue/error/success.

## State And Persistence
State is held in `struct private_auth_data`: GSS context, credential, names, mechanism, flags, output token, server string, and desired security. No persistence beyond process memory and external Kerberos credential caches used by GSS.

## Dependencies And Integration Points
Compiled only with `HAVE_LIBKRB5`. Depends on platform GSS headers, libnfs private RPC context, and RPC security enum values. `init.c` frees this auth data during context destruction.

## Risks
GSS calls are synchronous and comments note a helper thread may be needed for async-sensitive callers. The `nc_password` variable is currently unused, and cached credential behavior is noted as a TODO. Error formatting uses `asprintf`; partial allocation failures can return incomplete messages. Mechanism OID handling differs on Apple vs other platforms.

## Test Signals
Test Kerberos enabled and disabled builds, valid/invalid principals, missing credentials, KRB5/KRB5I/KRB5P flag selection, multi-token mutual auth, GSS error reporting, Apple and non-Apple mechanism paths, and cleanup after partial initialization failure.
