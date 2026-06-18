<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth.c -->
# sources/user-network-fs/samba/source4/auth/ntlm/auth.c

Purpose: core NTLM/auth4 framework: creates auth contexts, manages challenges, runs configured auth backends, logs auth events, creates session info, and registers auth modules.

Important APIs and types: `auth_context_set_challenge()` and `auth_get_challenge()` manage fixed or random 8-byte challenges. `auth_check_password_send/recv()` drives the async backend chain; `auth_check_password()` is the synchronous poll wrapper. `auth_context_create_methods()`, `auth_context_create()`, and `auth_context_create_for_netlogon()` build `auth4_context` objects with selected methods. `auth_register()`, `auth_backend_byname()`, `auth_interface_version()`, and `auth4_init()` implement module registration. Session wrappers include `auth_generate_session_info_wrapper()` and PAC-based `auth_generate_session_info_pac()`.

Control flow: password checking maps missing `mapped` names from client names, ensures a challenge, then walks `auth_method_context` entries. A backend may decline with `NT_STATUS_NOT_IMPLEMENTED` or non-authoritative failure, allowing the next method. The receive path logs success or failure with audit info and returns `auth_user_info_dc`. Session generation marks non-guest users authenticated, calls `auth_generate_session_info()`, and optionally fills Unix token info.

State and persistence: `auth4_context` stores event/message/loadparm/sam contexts, start time, challenge data, method list, netlogon flag, and function pointers used by upper layers. Backend registrations live in static global `backends` and `num_backends` initialized once.

Dependencies and integration: depends on tevent, Samba modules, samdb, winbind client, credentials, Kerberos PAC conversion, roles, auth logging, and Unix token helpers. It is the central integration point for anonymous, SAM, winbind, developer, LDAP simple bind, NTLMSSP, and GENSEC consumers.

Risks and test signals: the source declares `struct auth_check_password_wrapper *state` in `auth_check_password_wrapper_send()` while the actual state type is `struct auth_check_password_wrapper_state`; this is a build-time risk if not hidden by other declarations. Tests should cover backend ordering, non-authoritative fallback, challenge reuse, fixed challenge setup, audit logging, PAC session generation, role-specific default methods, netlogon-only method selection, duplicate backend registration, and static init idempotence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth.c -->
