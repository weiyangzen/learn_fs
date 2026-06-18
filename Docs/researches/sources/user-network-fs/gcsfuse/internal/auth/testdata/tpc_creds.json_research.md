<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/testdata/tpc_creds.json -->
# Research: sources/user-network-fs/gcsfuse/internal/auth/testdata/tpc_creds.json

Purpose: service-account credential fixture for a non-default Trusted Partner Cloud universe domain.

Important data and APIs: placeholder credential JSON includes `universe_domain: apis-tpclp.goog`, allowing tests to distinguish TPC from normal Google domain credentials.

Control flow and integration: `auth_test.go` verifies `getUniverseDomain` returns the TPC domain. Runtime key-file auth uses this distinction to select self-signed JWT access tokens instead of normal token exchange.

State and persistence: static non-secret test data; no external token service is contacted.

Dependencies: oauth2/google credential parsing and universe-domain support.

Risks: if non-default universe-domain credential schema changes, the fixture can become stale. The test only validates domain extraction, not end-to-end TPC access.

Test signals: `go test ./internal/auth -run TestAuthSuite/TestGetUniverseDomainForTPC`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/testdata/tpc_creds.json -->
