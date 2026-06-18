<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf.go -->
# sources/object-store/minio-mc/cmd/support-perf.go

Purpose: defines `mc support perf`, aggregates object/network/drive/client/site-replication performance results, renders JSON, and packages/upload results to SUBNET.

Important APIs/types/functions: `supportPerfCmd`, `supportPerfFlags`, `PerfTestOutput`, all result DTOs (`ObjTestResults`, `NetTestResults`, `DriveTestResults`, `ClientResult`, `SiteReplicationTestResults`), conversion helpers, `mainSupportPerf`, `execSupportPerf`, `runPerfTests`, `zipPerfResult`, and `savePerfResultFile`.

Control flow: `mainSupportPerf` accepts either `TARGET` for default tests or `TYPE TARGET` for a specific test. `execSupportPerf` initializes SUBNET connectivity/registration, runs requested tests, skips file upload for global JSON mode, then writes a JSON result plus `cluster.info` into a temporary zip. Airgapped mode moves it to `<alias>-perf_<timestamp>.zip`; online mode uploads to SUBNET and falls back to local save on upload failure. `runPerfTests` dispatches to per-test functions sequentially and collects one result per test.

State and persistence: writes temporary `mc-perf-*.zip`; final local zip is preserved in airgapped or upload-failure cases. Object speed tests may mutate server buckets through hidden flags; packaging includes cluster registration info.

Dependencies and integration points: depends on SUBNET upload helpers, MinIO admin perf APIs via sibling files, `madmin` result structs, JSON/zip standard libraries, and global output flags.

Risks and test signals: the parent waits on `resultCh` after each interactive test, so child functions must always send a final result. Tests should cover type dispatch, default test order, conversion correctness, zip contents, upload fallback, and JSON-mode no-upload behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf.go -->
