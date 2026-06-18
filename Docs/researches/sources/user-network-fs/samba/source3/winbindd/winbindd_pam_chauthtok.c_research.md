# sources/user-network-fs/samba/source3/winbindd/winbindd_pam_chauthtok.c

## sources/user-network-fs/samba/source3/winbindd/winbindd_pam_chauthtok.c

`winbindd_pam_chauthtok.c` is the parent asynchronous wrapper for plaintext PAM password changes (`WINBINDD_PAM_CHAUTHTOK`). It canonicalizes the target user, sends old and new passwords to the correct domain child, and maps child password-policy/reject details into the legacy response.

`winbindd_pam_chauthtok_send()` terminates the username, applies `normalize_name_unmap()`, canonicalizes the user with `canonicalize_username()`, resolves the target with `find_domain_from_name(namespace)`, and fills `wbint_PamAuthChangePassword` with client pid, flags, client name, canonical user, old password, and new password. It sends `dcerpc_wbint_PamAuthChangePassword_r_send()` to the domain child. The callback only receives the wrapped RPC result and completes the parent tevent request.

`winbindd_pam_chauthtok_recv()` calls `set_auth_errors()` with the child result, copies password policy fields from returned `samr_DomInfo1` via `fill_in_password_policy()`, stores the reject reason, and, for cached-login requests, updates in-memory single sign-on credentials with `winbindd_replace_memory_creds()`, ignoring missing memory creds as a common expired-password login case.

No durable state is directly stored here, but child-side password changes can update domain credentials and cached credentials, while this wrapper updates memory creds. Dependencies include generated wbint stubs, global event context, username canonicalization, domain routing, SAMR policy structures, and auth-error mapping. Risks include cleartext password lifetime, canonicalization selecting the wrong domain, missing domain returning `NO_SUCH_USER`, memory-cred update failure after a successful password change, and policy/reject information only being available when the child could retrieve it. Test signals include successful change, wrong old password, password restriction with reject reason, unsupported domain, cached-login memory cred replacement, and mapped username input.
