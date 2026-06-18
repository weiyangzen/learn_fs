# sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-ldap.c

Purpose: implements LDAP extended-operation submission to z/OS Remote-services for audit events.

Important APIs and data: exports `zos_remote_init`, `zos_remote_destroy`, `submit_request_s`, and `zos_remote_err2string`. Internal response structs capture overall and per-item major/minor codes. The core send path is `submit_xop_s`, with BER decoding in `decode_response`.

Control flow: initialization duplicates connection settings, creates an LDAP handle, and ensures LDAPv3. Submission flattens a BER request, connects/binds if necessary, sends the ICTX audit request extended operation, waits with configured timeout, validates the LDAP result and response OID, decodes BER response, logs per-item warnings/errors, and retries once on retryable connection failure.

State and persistence: `ZOS_REMOTE` stores server/user/password, LDAP handle, timeout, and connected flag. No disk persistence; connection state is recreated on retry or destroy.

Dependencies and integration: depends on OpenLDAP/liblber, OIDs and constants from `zos-remote-ldap.h`, config from `zos-remote-config.c`, and logging/debug helpers. It is called by the zOS plugin event submission thread.

Risks: LDAP simple bind uses plaintext password unless protected externally. Response allocation paths are complex; a `realloc` failure check uses `errno` rather than the returned pointer. Deprecated LDAP path contains a likely missing comma in `ldap_init` call under `LDAP_DEPRECATED`.

Test signals: LDAP integration tests should cover bind success/failure, timeout, server-down retry, bad OID, invalid BER version, per-item major code logging, and memory cleanup on errors.
