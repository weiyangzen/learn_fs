## sources/user-network-fs/samba/source4/kdc/kpasswd-service-heimdal.c

Purpose: Heimdal-flavoured request handler for the authenticated kpasswd payload after `kpasswd-service.c` has accepted and unwrapped the AP-REQ. It implements version 1 password change and RFC3244/Microsoft set-password semantics, then formats an authenticated kpasswd reply.

Important APIs and functions: `kpasswd_handle_request()` obtains `auth_session_info` from GENSEC, rejects TGT misuse with `kpasswd_check_non_tgt()`, then dispatches to `kpasswd_change_password()` for `KRB5_KPASSWD_VERS_CHANGEPW` or `kpasswd_set_password()` for `KRB5_KPASSWD_VERS_SETPW`. `kpasswd_change_password()` requires an initial ticket via `gensec_krb5_initial_ticket()` and delegates the actual SAMDB update to `samdb_kpasswd_change_password()`. `kpasswd_set_password()` decodes `ChangePasswdDataMS`, converts the password from UTF-8 to UTF-16, builds/unparses target principals, classifies service principals by component count, and calls `kpasswd_samdb_set_password()`.

Control flow: malformed set-password ASN.1 yields a kpasswd authenticated error reply rather than a transport failure. Missing target realm/name pairs are rejected as malformed. If no target principal is supplied, set-password falls back to self password change. For target principal changes, the function always builds a normal password-change reply using the NTSTATUS/reject reason from SAMDB.

State and persistence: no durable state is held locally; password changes persist through SAMDB helper calls. Per-request state is talloc-scoped, with Heimdal allocated structures released by `free_ChangePasswdDataMS()` and `krb5_free_principal()`.

Dependencies and integration: depends on Heimdal generated `ChangePasswdDataMS` decode/free helpers, GENSEC Kerberos ticket properties, Samba loadparm iconv handles, `kpasswd-helper`, and `kpasswd_glue`.

Risks: target principal parsing and service-principal classification affect whether SAMDB treats a password set as a user or service account operation. String conversion failure returns hard kpasswd errors. Initial-ticket enforcement is security critical for self-service password changes.

Test signals: exercise change-password with non-initial and initial tickets, RFC3244 set-password with and without target realm/name, malformed ASN.1, service principal targets, and password-policy rejection strings/dominfo mapping.
