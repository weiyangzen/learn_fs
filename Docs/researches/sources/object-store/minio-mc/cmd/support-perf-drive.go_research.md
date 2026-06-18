<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf-drive.go -->
# sources/object-store/minio-mc/cmd/support-perf-drive.go

Purpose: runs server-side drive speed tests for `mc support perf drive`.

Important APIs/types/functions: `mainAdminSpeedTestDrive` parses `blocksize`, `filesize`, and `serial`, calls `AdminClient.DriveSpeedtest`, and emits typed `PerfTestResult` values containing `[]madmin.DriveSpeedTestResult`.

Control flow: the command validates positive byte sizes, invokes the admin API with `madmin.DriveSpeedTestOpts`, then branches on global JSON mode. JSON mode drains versioned results from the result channel and prints converted output. Interactive mode starts the shared speed-test Bubble Tea UI, forwards progress events when result frames lack `Version`, accumulates final versioned drive results, sends a final message, and optionally writes to `outCh`.

State and persistence: no direct persistence; final results can be bundled by the parent support perf command.

Dependencies and integration points: depends on `go-humanize` parsing, MinIO admin drive speedtest, shared perf conversion types, and speed-test UI messaging.

Risks and test signals: size parsing, zero/negative validation, API errors before channel creation, and result frames without `Version` are important edge cases. Tests should check JSON output for API errors and that all versioned drive endpoint results survive conversion.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf-drive.go -->
