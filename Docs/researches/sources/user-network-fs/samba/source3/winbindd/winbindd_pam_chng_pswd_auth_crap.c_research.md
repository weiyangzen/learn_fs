# sources/user-network-fs/samba/source3/winbindd/winbindd_pam_chng_pswd_auth_crap.c

## sources/user-network-fs/samba/source3/winbindd/winbindd_pam_chng_pswd_auth_crap.c

`winbindd_pam_chng_pswd_auth_crap.c` is the parent wrapper for `WINBINDD_PAM_CHNG_PSWD_AUTH_CRAP`, a password-change command that sends pre-encrypted NT/LM password blobs rather than plaintext old/new passwords. It marshals the legacy request into `wbint_PamAuthCrapChangePassword` and delegates the real SAMR work to the domain child.

`winbindd_pam_chng_pswd_auth_crap_send()` terminates user and domain fields, derives the target domain from the explicit request domain or `lp_workgroup()` when `winbind use default domain` is enabled, resolves it with `find_domain_from_name()`, and rejects missing domains as `NO_SUCH_USER`. It fills client pid/name, domain, user, new NT password blob, encrypted old NT hash blob, and optional LM blobs. Empty LM length produces `data_blob_null` for both LM fields. It sends `dcerpc_wbint_PamAuthCrapChangePassword_r_send()` to the domain child and completes on callback.

`winbindd_pam_chng_pswd_auth_crap_recv()` maps transport errors immediately, otherwise sets auth errors from `state->r.out.result`, marks the response pending, and returns the encoded auth NTSTATUS. There is no file-local persistence; child-side behavior may change the password on the DC but refuses this mode when offline logons are enabled to avoid inconsistent cached credentials.

Dependencies include generated wbint stubs, global event context, talloc DATA_BLOB creation, domain routing, loadparm default-domain behavior, and `set_auth_errors()`. Risks include insufficient explicit length validation for blob fields beyond fixed request buffers, domain derivation ambiguity when no domain is supplied, legacy LM data handling, and limited policy feedback compared with plaintext chauthtok. Test signals include explicit and default-domain requests, NT-only and NT+LM blob changes, unknown domain, child failure mapping, and offline-logon refusal in the child implementation.
