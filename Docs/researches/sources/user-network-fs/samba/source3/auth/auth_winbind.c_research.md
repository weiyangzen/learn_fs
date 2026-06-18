# sources/user-network-fs/samba/source3/auth/auth_winbind.c

## Purpose
This file implements the `winbind` auth backend, delegating challenge/response authentication for remote or trusted domains to winbindd through libwbclient.

## Important APIs, Types, and Functions
The key checker is `check_winbind_security`; `auth_init_winbind` creates the backend and `auth_winbind_init` registers it. It uses `wbcAuthUserParams`, `wbcAuthUserInfo`, and `wbcAuthErrorInfo`.

## Control Flow
The checker rejects missing inputs and local-SAM domains so other modules can handle them. It populates a response-level winbind auth request with the client-supplied account/domain/workstation, logon parameters, NTLM challenge, NT and LM responses, and the netlogon flag when required. It calls `wbcAuthenticateUserEx` as root, maps winbind error cases to NTSTATUS, falls back to local SAM for non-authoritative no-such-user, and converts successful winbind info to server info.

## State and Persistence
No file-local state is stored. The call can depend on winbindd caches and trusted-domain passdb configuration. Successful server info records `nss_token` if username mapping occurred.

## Dependencies and Integration Points
Dependencies include libwbclient, passdb trusted-domain enumeration, server-role configuration, source3 server-info conversion, and the auth backend registry. It sits in method chains for domain members and DCs where remote domain validation may be required.

## Risks and Test Signals
Risks include changing the domain name before NTLMv2 verification, mishandling winbind absence for roles where it is mandatory, incorrectly ignoring trusted domains, and fallback loops on non-authoritative errors. Tests should cover local-domain bypass, remote-domain success, winbind unavailable on member/DC with and without trusts, netlogon mode flagging, and authoritative/no-such-user behavior.
