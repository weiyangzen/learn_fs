# sources/sync-backup/kopia/internal/server/api_policies_test.go

Purpose: integration-tests policy APIs.

Important APIs/types/functions: `TestPolicies`.

Control flow: starts a repository server, uses API calls to read default/effective policies, write policy updates, list policies, and delete them while asserting responses.

State and persistence behavior: policy manifests persist in the temporary test repository.

Dependencies and integration points: validates policy package integration, API auth, JSON payloads, and route query parsing.

Risks and test signals: scheduling refresh side effects are not always directly asserted and should be covered by source-manager tests.
