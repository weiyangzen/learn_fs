<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_developer.c -->
# sources/user-network-fs/samba/source4/auth/ntlm/auth_developer.c

Purpose: developer-only auth backend `name_to_ntstatus` for testing obscure NTSTATUS values and status-to-DOS mappings. It is enabled only in developer builds by the wscript.

Important APIs: `name_to_ntstatus_want_check()` accepts all requests. `name_to_ntstatus_check_password()` interprets the username as either an `NT_STATUS...` symbolic code or a hexadecimal status value, returns that failure if non-OK, or builds a minimal anonymous-like successful `auth_user_info_dc` when the status is OK. Async send/recv wrappers expose it as an auth backend. `auth4_developer_init()` registers it.

Control flow: password material is ignored. The username controls the returned status. On success it allocates user info, sets one anonymous SID with default group flags, zero session keys, domain/account fields, empty profile/home strings, timestamps and counters at zero, and normal account flags.

State and persistence: no persistent state except backend registration. It intentionally manufactures auth state for tests rather than consulting SAM or winbind.

Dependencies and integration: depends on auth structures, security SID definitions, tevent, and NTSTATUS string conversion. Built as `auth4_developer` only when `DEVELOPER_MODE` is true.

Risks and test signals: this backend must never be enabled in production configurations. Tests should assert build gating, username-to-status parsing, successful fabricated session shape, and backend registration. Because `want_check` always accepts, method ordering can mask real auth backends in developer mode.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_developer.c -->
