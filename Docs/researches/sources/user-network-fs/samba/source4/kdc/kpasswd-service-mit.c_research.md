## sources/user-network-fs/samba/source4/kdc/kpasswd-service-mit.c

Purpose: MIT Kerberos variant of the decoded kpasswd request handler. It mirrors the Heimdal path but uses MIT decode APIs and a local simple ASN.1 fallback for RFC3244 set-password requests that omit optional target principal and realm.

Important APIs and functions: external `decode_krb5_setpw_req()` parses MIT set-password structures. `decode_krb5_setpw_req_simple()` manually reads `SEQUENCE`/context-0 octet-string password via Samba ASN.1 helpers. `kpasswd_change_password()` enforces initial-ticket use and calls `samdb_kpasswd_change_password()`. `kpasswd_set_password()` converts password bytes to UTF-16, validates target realm/name pairing, unparses MIT principals, calls `kpasswd_samdb_set_password()`, and always serializes `kpasswd_make_pwchange_reply()` on SAMDB outcomes. `kpasswd_handle_request()` performs session extraction, TGT rejection, and version dispatch.

Control flow: MIT parser success gives password and optional target principal. Parser failure falls back only to the simple no-target packet shape; if that also fails, the client receives `KRB5_KPASSWD_MALFORMED` in an authenticated reply. No target principal means self-change, preserving initial-ticket enforcement. Targeted set-password skips initial-ticket check and relies on SAMDB authorization from `session_info`.

State and persistence: local state is transient and talloc/krb5 allocated. Persistent changes are made only by `samdb_kpasswd_change_password()` or `kpasswd_samdb_set_password()`.

Dependencies and integration: uses MIT krb5 principal APIs, Samba ASN.1 utilities, GENSEC, `kpasswd-helper`, `kpasswd_glue`, loadparm iconv configuration, and SAMDB password helpers.

Risks: the fallback decoder intentionally accepts a minimal structure; tests must ensure it cannot accidentally accept malformed targeted requests. `target_principal_string` allocation uses MIT free semantics, while other strings are talloc/SAFE_FREE; ownership errors here would be crash-prone. Version constants differ from Heimdal names but must stay wire-compatible.

Test signals: compare MIT and Heimdal behaviour for the same wire payloads, especially no-target RFC3244, target realm-only/name-only rejects, service principal short-name unparse, password policy rejects, and GENSEC session failures.
