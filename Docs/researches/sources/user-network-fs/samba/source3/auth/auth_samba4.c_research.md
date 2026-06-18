# sources/user-network-fs/samba/source3/auth/auth_samba4.c

## Purpose
This file implements the `samba4` auth backend used to redirect source3 authentication and GENSEC setup into the source4 authentication stack, especially for AD DC behavior.

## Important APIs, Types, and Functions
Important functions include `new_server_id_task`, `free_task_id`, `check_samba4_security`, `prepare_gensec`, `make_auth4_context_s4`, `auth_init_samba4`, and `auth_samba4_init`. The static `task_id_tree` allocates unique task IDs for messaging identities.

## Control Flow
`check_samba4_security` builds an auth4 context through source4, sets the source3 challenge, calls `auth_check_password`, converts `auth_user_info_dc` to SamInfo3, and returns either raw info3/no-authz server info or full server info. `prepare_gensec` initializes source4 loadparm, event, messaging, server credentials, and GENSEC server context, then requests session-key and Unix-token features. `make_auth4_context_s4` creates a source4 auth context, optionally using forced methods from the module parameter.

## State and Persistence
Persistent in-process state is the static IDR tree of allocated task IDs. Returned `server_id` objects remove their IDs through a talloc destructor. The backend also stores optional `forced_samba4_methods` on the auth context. No disk persistence is performed here.

## Dependencies and Integration Points
Dependencies include source4 auth, source4 events/messaging, GENSEC, credentials, loadparm, Samba server IDs, and auth SAM reply conversion. This module provides auth, `prepare_gensec`, and `make_auth4_context` hooks so the generic source3 path delegates deeply into source4.

## Risks and Test Signals
Risks include task ID leaks, messaging context setup failures, inconsistent token generation between SMB and LDAP if hooks diverge, and incorrect handling of non-authoritative `NO_SUCH_USER` fallback. Tests should cover AD DC NTLM, NTLMSSP and Kerberos via source4 GENSEC, forced method parameters such as `samba4:sam`, pdbtest coverage for SamLogon-style output, and repeated context creation/destruction.
