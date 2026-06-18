# sources/user-network-fs/gcsfuse/tools/proxy_server/main_test.go

Purpose: unit test for injecting retry ids into proxied HTTP requests.

Important APIs/types/functions: `TestAddRetryID`.

Control flow: starts a mock server returning a retry test id, sets package globals `gConfig` and `gOpManager`, builds a request and request-type instruction, calls `AddRetryID`, and asserts the request header was populated.

State/persistence behavior: mutates package globals for the duration of the test and starts a temporary HTTP server.

Dependencies/integration: covers interaction among operation manager, emulator helper, and request mutation.

Risks/test signals: does not restore globals after the test; safe only if tests do not depend on pristine global state.
