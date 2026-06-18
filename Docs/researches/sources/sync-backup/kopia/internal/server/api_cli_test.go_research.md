# sources/sync-backup/kopia/internal/server/api_cli_test.go

Purpose: integration-tests the CLI info API through the HTTP API client.

Important APIs/types/functions: `TestCLIAPI`, `repotesting.NewEnvironment`, `servertesting.StartServer`, and `apiclient`.

Control flow: starts a test repository server, authenticates, fetches CSRF token, calls `GET cli`, and compares the executable/config command string with local expectations.

State and persistence behavior: creates a temporary test repository and server only for test lifetime.

Dependencies and integration points: covers API routing, auth, CSRF setup, and handler output.

Risks and test signals: assumes executable/config paths do not require quoting in this specific environment.
