<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top-api.go -->
# sources/object-store/minio-mc/cmd/support-top-api.go

Purpose: implements `mc support top api`, a real-time terminal summary of in-flight/API trace events.

Important APIs/types/functions: `supportTopAPIFlags`, `supportTopAPICmd`, `checkSupportTopAPISyntax`, and `mainSupportTopAPI`.

Control flow: after one-target validation and registration check, the command creates an admin client, builds trace options with `tracingOpts`, builds filters with `matchingOpts`, starts `client.ServiceTrace`, and forwards matching `madmin.ServiceTraceInfo` values into a buffered channel consumed by `initTraceStatsUI(false, 30, filteredTraces)`. Trace errors kill the UI and are reported after `Run`.

State and persistence: read-only streaming command; no persistent state.

Dependencies and integration points: depends on trace filtering helpers from the broader trace command implementation, MinIO admin service tracing, Bubble Tea UI in `trace-stats-ui.go`, and support registration.

Risks and test signals: long-lived goroutines and error propagation via captured `te` are sensitive to races. Tests should cover filter option construction, trace error handling, UI channel forwarding, and graceful cancellation.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top-api.go -->
