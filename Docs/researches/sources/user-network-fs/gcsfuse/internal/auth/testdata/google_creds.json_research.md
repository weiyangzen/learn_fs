<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/testdata/google_creds.json -->
# Research: sources/user-network-fs/gcsfuse/internal/auth/testdata/google_creds.json

Purpose: service-account credential fixture representing the default Google universe domain.

Important data and APIs: placeholder service-account JSON includes `universe_domain: googleapis.com` along with key, client, token, and certificate URL fields required by Google credential parsing.

Control flow and integration: `auth_test.go` reads it and verifies `getUniverseDomain` returns `UniverseDomainDefault`, which keeps `newTokenSourceFromPath` on the normal OAuth2 JWT token-source path.

State and persistence: static non-secret test credential data; no token is fetched during the test.

Dependencies: oauth2/google JSON credential schema and storage scope handling.

Risks: placeholder private key formatting must remain parseable by the library. If default universe-domain behavior changes, the expected domain may need updating.

Test signals: `go test ./internal/auth -run TestAuthSuite/TestGetUniverseDomainForGoogle`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/testdata/google_creds.json -->
