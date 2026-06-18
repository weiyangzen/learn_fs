# sources/sync-backup/kopia/internal/server/server_authz_checks_test.go

Purpose: tests CSRF token generation and validation.

Important APIs/types/functions: `TestGenerateCSRFToken` and `TestValidateCSRFToken`.

Control flow: constructs test server/options, generates expected tokens for session IDs, builds HTTP requests with cookies and headers, and asserts validation success/failure cases.

State and persistence behavior: in-memory server signing key and request cookies only.

Dependencies and integration points: protects UI API CSRF enforcement used by all mutating UI handlers.

Risks and test signals: should include disabled-CSRF option and missing cookie/header cases to guard request wrapper behavior.
