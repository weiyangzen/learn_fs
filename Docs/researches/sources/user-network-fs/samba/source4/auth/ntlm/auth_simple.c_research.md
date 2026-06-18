<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_simple.c -->
# sources/user-network-fs/samba/source4/auth/ntlm/auth_simple.c

Purpose: implements LDAP simple bind authentication on top of the auth4 password-check and session-info framework.

Important APIs: `authenticate_ldap_simple_bind_send()` builds an auth context, maps a DN or principal to NT4 domain/account with `crack_auto_name_to_nt4_name()`, prepares plaintext `auth_usersupplied_info`, and starts `auth_check_password_send()`. `authenticate_ldap_simple_bind_recv()` returns generated `auth_session_info`. The completion callback creates session info and logs authorization success with transport protection details.

Control flow: send allocates request state, records TLS use, remote/local addresses, service/auth descriptions, plaintext password, case-insensitive and no-Unix-account flags, and logon parameters allowing cleartext supplied passwords and trust accounts. Name cracking failures are logged immediately as authentication events. On password success, the callback sets default group/authenticated flags, calls `generate_session_info`, logs successful authz with TLS vs none, and completes.

State and persistence: per-request state holds auth context, user info, TLS flag, and resulting session info. It reads SAM through auth methods and may update accounting through `auth_sam.c`.

Dependencies and integration: depends on tevent, auth4, samdb name cracking, loadparm, tsocket addresses, and authz logging. It is the LDAP server's bridge from simple bind inputs to Samba authorization sessions.

Risks and test signals: cleartext password handling must be constrained by transport policy outside this function; this code records but does not enforce TLS. Tests should cover DN mapping, bad DN logging, TLS/non-TLS audit strings, trust-account logon parameters, wrong password, generated session flags for guest vs authenticated users, and remote/local address propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_simple.c -->
