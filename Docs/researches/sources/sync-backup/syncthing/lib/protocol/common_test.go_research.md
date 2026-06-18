## sources/sync-backup/syncthing/lib/protocol/common_test.go

Purpose: shared protocol test fixtures and helpers.

Important content: defines reusable fake request responses, mocked connection info, test keys/cert-like identifiers, or helper assertions used by protocol tests in the package.

Control flow and state: helper-only; state is generally package-level fixtures for tests.

Dependencies and integration points: consumed by connection, benchmark, encryption, and serialization tests.

Risks: shared helpers can hide assumptions or introduce coupling between tests if mutated globally.

Test signals: no direct tests; indirectly exercised by protocol test suite.
