<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/testdata/empty_creds.json -->
# Research: sources/user-network-fs/gcsfuse/internal/auth/testdata/empty_creds.json

Purpose: empty credential fixture used to prove universe-domain extraction reports a wrapped JSON parse error.

Important data and APIs: the file is intentionally empty JSON input for `google.CredentialsFromJSON`; it is consumed by `auth_test.go` rather than runtime code.

Control flow and integration: `TestGetUniverseDomainForEmptyCreds` reads the file and calls private `getUniverseDomain`, expecting `CredentialsFromJSON(): unexpected end of JSON input`.

State and persistence: static test data only; no credentials or token state.

Dependencies: oauth2/google credential parser error behavior and exact error wrapping.

Risks: dependency upgrades can change the underlying error string. The fixture must remain empty to test the intended failure.

Test signals: `go test ./internal/auth -run TestAuthSuite/TestGetUniverseDomainForEmptyCreds`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/testdata/empty_creds.json -->
