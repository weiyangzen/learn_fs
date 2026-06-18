# sources/sync-backup/kopia/internal/server/api_sources_test.go

Purpose: tests source API counters and refresh behavior.

Important APIs/types/functions: `TestSnapshotCounters` and `TestSourceRefreshesAfterPolicy`.

Control flow: creates test sources/snapshots or policies, calls source APIs, and asserts source manager counters/status refresh as expected.

State and persistence behavior: temporary repository manifests and runtime source-manager state.

Dependencies and integration points: validates interaction between policies, snapshots, source managers, and API responses.

Risks and test signals: asynchronous refresh can be timing-sensitive; tests should avoid sleeps where possible.
