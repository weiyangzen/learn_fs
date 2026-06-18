# sources/sync-backup/syncthing/cmd/infra/strelaypoolsrv/stats_test.go

Purpose: small unit test for the relay pool stats smoothing helper.

Important APIs/tests: `TestMerge` calls `mergeValue` with increasing, slightly decreasing, and sharply decreasing inputs.

Control flow and state: the test is stateless and directly validates the threshold policy: increases pass through, values within 1 percent below the old value are held at the old value, and large drops are treated as real resets.

Dependencies/integration: depends only on `testing` and the local helper in `stats.go`.

Risks and test signals: it documents the intended anti-spike behavior for Prometheus counters. It does not test `mergeStats`, per-field metric update behavior, or remote status scraping.
