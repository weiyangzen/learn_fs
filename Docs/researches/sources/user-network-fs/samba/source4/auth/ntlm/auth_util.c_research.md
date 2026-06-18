<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_util.c -->
# sources/user-network-fs/samba/source4/auth/ntlm/auth_util.c

Purpose: utility for converting user-supplied password material between plaintext, NT/LM hash, and NTLM challenge-response forms.

Important API: `encrypt_user_info(TALLOC_CTX *, struct auth4_context *, enum auth_password_state to_state, const struct auth_usersupplied_info *, const struct auth_usersupplied_info **out)` is the main exported helper. It creates shallow copies of `auth_usersupplied_info` with talloc references to preserve original lifetime while replacing password fields.

Control flow: conversion to response first converts plaintext to hashes if needed, gets the auth challenge, and then produces either NTLMv2 responses using `SMBNTLMv2encrypt_hash()` and generated names blob or NTLMv1/LM responses using `SMBOWFencrypt()` depending on loadparm client auth settings. Conversion to hash computes LM hash when possible with `E_deshash()` and NT hash with `E_md4hash()`. Unsupported conversions return `NT_STATUS_INVALID_PARAMETER`.

State and persistence: no global state. Returned user-info copies and generated blobs live under the provided memory context. Challenge data is obtained from `auth_context`, which may generate and persist a random challenge.

Dependencies and integration: used by SAM and winbind backends to normalize credentials before local checks or Netlogon SamLogon. Depends on libcli auth crypto, GnuTLS error mapping, loadparm NTLM policy, and challenge helpers.

Risks and test signals: there appears to be a likely bug in the LM branch where `SMBOWFencrypt()` writes into `blob.data` rather than `lm_blob.data`; tests should verify LM response bytes when LM auth is enabled. Other tests should cover NTLMv2 enabled/disabled, plaintext-to-hash, hash-to-response, missing LM hash fallback to NT response, crypto error mapping, invalid target states, and lifetime of shallow-copied strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_util.c -->
