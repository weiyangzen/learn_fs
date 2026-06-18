# sources/user-network-fs/gcsfuse/tools/proxy_server/emulator_test.go

Purpose: unit tests for retry-test creation client behavior.

Important APIs/types/functions: `TestGetRetryID` and `TestCreateRetryTest`.

Control flow: mock HTTP servers assert `/retry_test`, return JSON id values, and tests assert expected ids. Empty instruction input is checked for no-op behavior.

State/persistence behavior: starts temporary HTTP servers; no durable state.

Dependencies/integration: uses `httptest` and `testify/assert`.

Risks/test signals: tests do not cover non-200 responses, malformed JSON responses, or invalid host URLs.
