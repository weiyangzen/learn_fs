<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/kerberos_credentials.h -->
# sources/user-network-fs/samba/source4/auth/kerberos/kerberos_credentials.h

Purpose: small public header for Kerberos credential helper functions used by GENSEC and authentication callers that need to convert Samba credentials into Kerberos principals or credential caches without including broader internal implementation details.

Important APIs: `kinit_to_ccache()` obtains Kerberos initial credentials into a supplied ccache using `cli_credentials`, an `smb_krb5_context`, loadparm context, tevent context, and returns credential provenance plus an error string. `principal_from_credentials()` parses the Kerberos principal implied by `cli_credentials` and reports how the credential was obtained.

Control flow and state: the header has no direct state. The API signatures reveal that callers provide the destination cache and event context; the implementation may perform network KDC operations and set event hooks on Heimdal contexts while acquiring tickets.

Dependencies and integration: depends on `struct cli_credentials`, `struct smb_krb5_context`, `struct loadparm_context`, `struct tevent_context`, and Samba credential provenance enum definitions. It bridges auth credential storage with Kerberos ticket acquisition.

Risks and test signals: consumers should check both return code and `error_string`. Tests need password, keyblock/NT-hash, FAST armor, S4U impersonation, missing-principal, and clock-skew cases. Build tests should ensure this header remains light enough for callers that do not otherwise use raw krb5 APIs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/kerberos_credentials.h -->
