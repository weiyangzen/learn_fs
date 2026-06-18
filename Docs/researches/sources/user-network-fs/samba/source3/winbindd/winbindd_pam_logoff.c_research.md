# sources/user-network-fs/samba/source3/winbindd/winbindd_pam_logoff.c

## sources/user-network-fs/samba/source3/winbindd/winbindd_pam_logoff.c

`winbindd_pam_logoff.c` is the parent asynchronous wrapper for `WINBINDD_PAM_LOGOFF`. Its purpose is to authorize a logoff request, delegate Kerberos ccache cleanup to the domain child, and remove winbind memory credentials on success.

`winbindd_pam_logoff_send()` terminates username and krb5 ccache fields, rejects invalid uid, canonicalizes the username, resolves the auth domain with `find_auth_domain()`, and checks the peer process credentials via `getpeereid(cli->sock, &caller_uid, &caller_gid)`. Root may log off any user; non-root callers must match `request->data.logoff.uid`. It then fills `wbint_PamLogOff` with client name/pid, flags, canonical user, uid, and ccache name, and sends `dcerpc_wbint_PamLogOff_r_send()` to the child.

`winbindd_pam_logoff_recv()` maps errors through `set_auth_errors()`, marks the response pending, and, when the child result is OK, deletes memory credentials for the user in the parent with `winbindd_delete_memory_creds()`. The child-side `_wbint_PamLogOff()` checks Kerberos flags and ccache identity before removing ccache and memory creds in the child.

Persistent effects are ccache-list removal and memory-credential deletion; no on-disk state is managed here directly. Dependencies include peer credential APIs, username canonicalization, domain routing, generated wbint stubs, global event context, and memory credential helpers. Risks include platform behavior of `getpeereid()`, uid truncation/invalid uid handling, canonicalization mismatches, and ensuring a caller cannot remove another user's ccache. Test signals include root and same-uid logoff, different-uid rejection, missing/blank ccache success, Kerberos and non-Kerberos flags, memory credential deletion, and unknown user/domain handling.
