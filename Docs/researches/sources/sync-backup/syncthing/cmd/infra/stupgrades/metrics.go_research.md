# sources/sync-backup/syncthing/cmd/infra/stupgrades/metrics.go

Purpose: centralizes Prometheus collectors for the upgrade metadata service.

Important APIs/state: `metricUpgradeChecks`, `metricFilterCalls`, `metricHTTPRequests`, and `metricLatestReleaseInfo` are registered with `promauto` under namespace `syncthing` and subsystem `upgrade`.

Control flow: collectors are initialized at package load. Runtime updates come from `serveReleases`, compatibility filtering, GitHub/compat/proxy HTTP fetches, and `cachedReleases.Update`.

State and persistence: all state is in-process Prometheus collector state; `metricLatestReleaseInfo` uses labels for latest stable and prerelease versions and is explicitly deleted/replaced on cache changes.

Dependencies/integration: depends on Prometheus client packages and the functions in `main.go`.

Risks and test signals: label cardinality is bounded by configured forward names and release version labels. There are no tests here; correctness is observed indirectly via metrics endpoint and service behavior.
