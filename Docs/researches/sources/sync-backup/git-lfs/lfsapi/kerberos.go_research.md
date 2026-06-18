# sources/sync-backup/git-lfs/lfsapi/kerberos.go

Purpose: Handles Negotiate authentication path for API requests.

Important APIs/types/functions: `Client.doWithNegotiate`.

Control flow: When access mode is `creds.NegotiateAccess`, the client delegates to `doWithAccess` with Negotiate mode, allowing the lower HTTP transport to use SPNEGO. NTLM is explicitly not supported by this path.

State and persistence behavior: No direct state mutation beyond the delegated HTTP request.

Dependencies and integration points: Integrates with `creds.CredentialHelperWrapper`, `creds.NegotiateAccess`, and `lfshttp.Client.Transport`, which wraps transport with `spnego.Transport` for negotiate mode.

Risks and edge cases: `credWrapper` is unused here; any future NTLM or credential material handling would need explicit implementation. SPNEGO errors are converted to auth errors in `lfshttp`.

Test signals: Covered indirectly by auth mode selection tests; no real Kerberos integration test in this subset.
