# sources/user-network-fs/samba/source4/auth/auth.h

## Purpose

This header defines the Samba4 authentication backend interface and exports the core auth/session helpers used by source4 services and GENSEC integration. It standardizes how auth modules advertise password-check operations, how auth contexts are created, and how authenticated users are converted into `auth_session_info`.

## Important APIs, Types, And Functions

The primary interface type is `struct auth_operations`, with `name`, `want_check()`, `check_password_send()`, and `check_password_recv()` members. `want_check()` lets a backend claim or decline a supplied login attempt. The send/recv pair implements asynchronous password verification through `tevent_req`, returning interim domain controller user info, client/server audit records, and an authoritative flag.

`struct auth_method_context` links a backend into an auth context and stores `auth_ctx`, `ops`, recursion `depth`, and backend `private_data`. `struct auth_critical_sizes` records ABI-sensitive structure sizes and the `AUTH4_INTERFACE_VERSION`, which is currently zero for the unstable Samba4 interface.

Exported helpers include `encrypt_user_info()`, `auth_get_challenge()`, `authsam_account_ok()`, `authsam_make_user_info_dc()`, `authsam_update_user_info_dc()`, `authsam_shallow_copy_user_info_dc()`, `auth_system_session_info()`, `auth_context_create_methods()`, `auth_methods_from_lp()`, `auth_context_create()`, `auth_context_create_for_netlogon()`, synchronous and asynchronous `auth_check_password()` variants, `auth_context_set_challenge()`, `auth4_init()`, `auth_register()`, `server_service_auth_init()`, LDAP simple bind authentication send/recv/sync helpers, and `samba_server_gensec_start()`/`samba_server_gensec_krb5_start()`.

## Control Flow

The header itself has no executable flow, but it defines the expected flow. Server code creates an `auth4_context` from configured methods, asks each backend whether it wants to check the supplied info, starts an asynchronous password check, and receives an `auth_user_info_dc` result plus audit metadata. Session creation helpers then turn account data, PAC data, or system credentials into `auth_session_info`.

GENSEC server setup flows through `samba_server_gensec_start()` or the Kerberos-specific wrapper, passing event/messaging/loadparm contexts, server credentials, and target service into the GENSEC layer.

## State And Persistence

State is carried in caller-owned contexts and talloc-owned structures: auth contexts, method contexts, supplied user info, interim domain user info, session info, and backend `private_data`. The header does not define persistent storage, but declared functions integrate with SAM/ldb, generated NDR types, loadparm configuration, credentials, challenges, and audit structures.

## Dependencies And Integration Points

The header includes PAC and auth NDR definitions plus common auth declarations, then pulls in session, Unix token, system session, and security headers. Forward declarations connect it to `ldb`, `loadparm_context`, `imessaging_context`, `gensec_security`, `cli_credentials`, `smb_krb5_context`, and tsocket addresses. It is included by GENSEC Kerberos implementations to generate session information after ticket/PAC verification and by source4 services that need password or LDAP bind authentication.

## Risks And Edge Cases

The ABI/interface version is explicitly unstable, so modules compiled against this interface are sensitive to structure changes. Async auth implementations must return authoritative information correctly; mistakes can cause fallback or lockout behavior to be wrong. Session key and PAC integration is security-sensitive because downstream SMB/RPC signing and authorization depend on correct `auth_session_info`. LDAP simple bind APIs must preserve TLS and remote/local address context for policy and auditing.

## Test Signals

Good signals include unit and integration tests for auth module registration, configured method ordering, challenge generation, password check send/recv behavior, LDAP simple binds with and without TLS, account policy checks, SAM-derived session info, system sessions, netlogon-specific contexts, and GENSEC server startup using Kerberos credentials.
