<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_anonymous.c -->
# sources/user-network-fs/samba/source4/auth/ntlm/auth_anonymous.c

Purpose: implements the `anonymous` auth4 backend, which accepts only empty anonymous credentials and produces anonymous `auth_user_info_dc`.

Important APIs: `anonymous_want_check()` decides whether a request is anonymous by checking empty account name and empty plaintext/hash/response credentials. `anonymous_check_password_send/recv()` returns `auth_anonymous_user_info_dc()` output through tevent. `auth4_anonymous_init()` registers the backend.

Control flow: nonempty account names or password material return `NT_STATUS_NOT_IMPLEMENTED`, allowing later backends to try. Empty acceptable anonymous input creates a tevent request, builds anonymous user info with the configured NetBIOS name, posts completion, and returns the interim info in recv.

State and persistence: no global state beyond backend registration. Each request stores only a temporary `auth_user_info_dc`. Audit info outputs are NULL.

Dependencies and integration: depends on `auth/auth.h`, generated auth prototypes, loadparm NetBIOS name, tevent, and tevent NTSTATUS helpers. Default auth method lists put this backend first so anonymous logons are handled consistently.

Risks and test signals: the LM response special case permits a single zero byte as anonymous but rejects other nonempty responses. Tests should cover plaintext empty vs nonempty, hash pointers present/absent, NT response length, no account name, backend registration collision, and ordering before SAM/winbind.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_anonymous.c -->
