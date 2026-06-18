# sources/user-network-fs/samba/source3/auth/auth_generic.c

## Purpose
This file adapts source3 authentication to the source4 `auth4_context` and GENSEC server interfaces. It prepares NTLMSSP/SPNEGO/Kerberos/SCHANNEL authentication and converts successful password or PAC validation into `auth_session_info`.

## Important APIs, Types, and Functions
Key functions are `make_auth4_context`, `auth_generic_prepare`, and `auth_check_password_session_info`. Internal PAC/Kerberos helpers are `generate_pac_session_info`, `generate_krb5_session_info`, `auth3_generate_session_info_pac`, and `make_auth4_context_s3`.

## Control Flow
For Kerberos PACs, domain-member/DC roles send the PAC to winbind through `wbcAuthenticateUserEx` and build server/session info from the returned identity. Standalone mode parses a minimal PAC, rejects full logon-info PACs, maps the Kerberos principal to a local user, and calls `make_session_info_krb5`. `auth_generic_prepare` either delegates to a backend-provided `prepare_gensec` hook or builds source3 GENSEC settings, orders Kerberos before NTLMSSP, adds SPNEGO/SCHANNEL/local-system mechanisms, sets anonymous server credentials, then attaches remote/local addresses and service description.

## State and Persistence
The code allocates short-lived talloc frames and moves resulting contexts to caller ownership. It may prime winbind/netsamlogon caches through PAC authentication. It sets current user substitution state and reloads shares after successful PAC or NTLM auth so `%U`-dependent configuration reflects the authenticated user.

## Dependencies and Integration Points
Dependencies include GENSEC, Kerberos/PAC NDR structures, winbind client APIs, loadparm, credentials, tsocket, PAM account checking, and source3 auth3 functions from `auth_ntlmssp.c`. It is the key integration layer used by SMB, RPC, and other services needing generic security negotiation.

## Risks and Test Signals
Risks include winbind unavailability, incorrect role-specific PAC handling, missing DNS names, GENSEC backend ordering regressions, and session-info mismatches between Kerberos and NTLM paths. Test signals include Kerberos PAC validation, standalone MIT realm mapping, NTLMSSP negotiation, SPNEGO fallback, SCHANNEL/local-system behavior, PAM account denial after PAC validation, and authorization audit events from `auth_check_password_session_info`.
