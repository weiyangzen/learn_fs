<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf-net.go -->
# sources/object-store/minio-mc/cmd/support-perf-net.go

Purpose: runs MinIO network throughput tests for `mc support perf net`.

Important APIs/types/functions: `mainAdminSpeedTestNetperf` parses a duration, calls `AdminClient.Netperf`, and converts `madmin.NetperfResult` into support performance output.

Control flow: the function builds an admin client, creates a cancellable context, validates positive duration, and starts a goroutine that calls `client.Netperf`. JSON mode selects the first error or result and prints converted `PerfTestOutput`. Interactive mode starts the shared speed-test UI and sends empty progress updates until a final result/error arrives, then forwards the final `PerfTestResult` to the UI and optional parent channel.

State and persistence: no direct persistence; parent `support-perf.go` may archive/upload the result.

Dependencies and integration points: depends on MinIO admin network perf API, `PerfTestResult`, `NetPerfTest`, conversion functions, and Bubble Tea UI.

Risks and test signals: select behavior with closed channels and long-running server calls are the main control-flow risks. Tests should cover invalid duration, admin API error, JSON result conversion, and interactive finalization.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf-net.go -->
