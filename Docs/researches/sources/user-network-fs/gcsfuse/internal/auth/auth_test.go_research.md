<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/auth_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/auth/auth_test.go

Purpose: validates universe-domain extraction used by key-file token-source selection.

Important APIs/types/functions: `AuthTest` testify suite, `TestGetUniverseDomainForGoogle`, `TestGetUniverseDomainForTPC`, and `TestGetUniverseDomainForEmptyCreds`.

Control flow: tests read fixture JSON files, call private `getUniverseDomain`, and assert either default `googleapis.com`, TPC `apis-tpclp.goog`, or a wrapped JSON parse error.

State and persistence: fixture-only reads; no external token exchange or credential persistence.

Dependencies: storage full-control scope, oauth2/google credential parsing, testify suite/assertions, and JSON fixtures under `internal/auth/testdata`.

Risks: fixture private keys are placeholders, but schema must remain parseable by Google libraries. Exact error-string assertions may drift with dependency upgrades.

Test signals: run `go test ./internal/auth -run AuthSuite` after changing credential parsing or universe-domain support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/auth_test.go -->
