# sources/user-network-fs/samba/source3/winbindd/winbindd_pam_auth_crap.c

## sources/user-network-fs/samba/source3/winbindd/winbindd_pam_auth_crap.c

`winbindd_pam_auth_crap.c` is the parent asynchronous wrapper for `WINBINDD_PAM_AUTH_CRAP`, Samba's NTLM challenge/response authentication command. It also supports PAC-auth verification when `WBFLAG_PAM_AUTH_PAC` is set. State tracks authoritative status, flags, PAC trust, domain/user strings, child validation, and the child result.

The send path handles two modes. PAC mode calls `winbindd_pam_auth_pac_verify()` locally in the parent, stores validation and trusted status, and completes without a domain child. NTLM mode terminates request strings, validates request flags with `check_request_flags()`, resolves the auth domain (defaulting blank domain to `lp_workgroup()`), checks LM/NT response lengths including the `WBFLAG_BIG_NTLMV2_BLOB` extra-data path, parses required membership SIDs, copies LM/NT responses and the 8-byte challenge into DATA_BLOBs, then calls `dcerpc_wbint_PamAuthCrap_send()` on the domain child.

`winbindd_pam_auth_crap_recv()` propagates transport and child errors via `set_auth_errors()`, appends requested keys/Info3/AFS data with `append_auth_data()`, conditionally suppresses trusted-domain addition for untrusted PACs, adds trusted-domain data for Info3 text, sets `response->data.auth.authoritative`, marks the response pending, and returns the encoded auth NTSTATUS.

There is no file-local persistence. Effects include cache priming in PAC verification when trusted and child-side SamLogon/cache updates. Dependencies include Netlogon utility types, generated wbint stubs, global event context, `extra_data_to_sid_array()`, `append_auth_data()`, and domain routing. Risks include length validation for large NTLMv2 blobs, authoritative semantics for unknown domains, PAC data being accepted but not cache-primed when untrusted, and NULL validation assumptions after child failures. Test signals include NTLMv1/NTLMv2/big-blob inputs, unknown-domain non-authoritative response, required group rejection, PAC verified/unverified behavior, and response auth flags.
