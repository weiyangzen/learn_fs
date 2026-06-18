<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf-client.go -->
# sources/object-store/minio-mc/cmd/support-perf-client.go

Purpose: runs the client-to-server performance test used by `mc support perf client` and by the default support performance bundle.

Important APIs/types/functions: `mainAdminSpeedTestClientPerf` creates an admin client, parses the hidden `duration` flag, calls `AdminClient.ClientPerf`, and emits `PerfTestResult` messages.

Control flow: after duration validation, a goroutine calls `client.ClientPerf` and sends either an error or `madmin.ClientPerfResult`. In JSON mode, the first result/error is converted to `PerfTestOutput` and printed. In interactive mode, a Bubble Tea speed-test UI is started; a second goroutine sends periodic empty progress messages every 100 ms until the final result/error arrives, then forwards the final `PerfTestResult` to the UI and optional aggregation channel.

State and persistence: no local persistence. Results may be accumulated by `support-perf.go` and later zipped/uploaded.

Dependencies and integration points: depends on admin client construction, `madmin.ClientPerf`, `PerfTestResult`, `ClientPerfTest`, `convertPerfResult`, and `initSpeedTestUI` from nearby perf UI code.

Risks and test signals: unbuffered channel sequencing and closed error/result channels can produce zero-value results if not carefully handled. Tests should validate duration errors, JSON error output, final-result forwarding to `outCh`, and UI progress behavior under delayed server responses.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf-client.go -->
