# sources/user-network-fs/samba/source3/auth/auth.c

## Purpose
This file is the source3 NTLM authentication dispatcher. It registers auth backends, creates role-specific `auth_context` method chains, manages NTLM challenges, and runs user-supplied credentials through the configured backend list.

## Important APIs, Types, and Functions
The backend registry is the static `auth_backends` list of `auth_init_function_entry`. Public functions include `smb_register_auth`, `auth_get_ntlm_challenge`, `auth_check_ntlm_password`, `make_auth3_context_for_ntlm`, `make_auth3_context_for_netlogon`, `make_auth3_context_for_winbind`, and `auth3_context_set_challenge`. Internal helpers include `check_domain_match`, `make_auth_context`, `load_auth_module`, `make_auth_context_text_list`, and `make_auth_context_specific`.

## Control Flow
Backends register by name and interface version. Context creation chooses a method string from `lp_server_role()` and settings such as `lp_encrypt_passwords()`, then loads static/probed modules and links them into `auth_method_list`. During authentication, `auth_check_ntlm_password` validates the challenge, enforces trusted-domain policy, iterates methods until one returns something other than `NT_STATUS_NOT_IMPLEMENTED`, optionally performs a PAM account check, logs authentication events, and returns `auth_serversupplied_info`.

## State and Persistence
Process-local state includes the global backend registry, per-context challenge blob, `challenge_set_by`, `start_time`, method private data, and `for_netlogon`. Persistent external state is not written here, but called backends may update passdb and PAM/account state. The context destructor frees each method's private data.

## Dependencies and Integration Points
The dispatcher depends on loadparm configuration, dynamic Samba module probing, messaging for audit events, tsocket remote addresses, PAM account checks, and backend modules such as anonymous, SAM, winbind, samba4, and unix. It bridges to source4/GENSEC through method hooks selected from the first method that exposes them.

## Risks and Test Signals
Risks include wrong role-to-method selection, challenge length mismatches, module registration collisions, unexpected non-authoritative fallback, and PAM/account check failures after password success. Test signals include authentication event logs, role-specific auth method ordering, trusted-domain denial, `NT_STATUS_NOT_IMPLEMENTED` fallback behavior, guest/non-guest success logging, and failure authoritative flags.
