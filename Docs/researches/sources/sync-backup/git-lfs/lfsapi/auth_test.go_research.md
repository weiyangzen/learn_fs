# sources/sync-backup/git-lfs/lfsapi/auth_test.go

Purpose: Validates authenticated API behavior and credential selection across challenge modes, retries, URL sources, and redirects.

Important APIs/types/functions: Tests `getAuthAccess`, `DoWithAuth`, `DoWithAuthNoRetry`, `DoAPIRequestWithAuth`, `getCreds`, mock credential helpers, multistage helper behavior, and redirect reauthentication.

Control flow: HTTP test servers return 401, challenge headers, redirects, or success. Mock helpers fill, approve, reject, or preserve multistage state. Table-driven credential tests construct contexts with endpoint, remote, header, and config variations, then assert `Authorization`, helper input, and chosen credential URL.

State and persistence behavior: In-memory mock helpers track approved credentials keyed by protocol/host/path. Client endpoint access mode mutates from `none` to `basic` or `negotiate` after challenges.

Dependencies and integration points: Uses `httptest`, `git.NewReadOnlyConfig`, `lfshttp.NewContext`, `creds.CredentialCacher`, and `lfsapi.Client` credential wrappers.

Risks and edge cases: Covers avoiding retry when an explicit Authorization header is rejected, retry exhaustion, multistage helpers that never advance state, and reauthentication when redirects cross hosts.

Test signals: High confidence for auth retry semantics and credential source precedence. It does not exercise real external credential helpers or real Kerberos/SPNEGO negotiation.
