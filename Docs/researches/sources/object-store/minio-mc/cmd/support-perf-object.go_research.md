<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf-object.go -->
# sources/object-store/minio-mc/cmd/support-perf-object.go

Purpose: runs object PUT/GET performance tests for `mc support perf object` and keeps the hidden legacy `admin speedtest` command deprecated.

Important APIs/types/functions: `adminSpeedtestCmd`, `mainAdminSpeedtest`, and `mainAdminSpeedTestObject`. The object test parses `duration`, `size`, `concurrent`, `bucket`, `noclear`, and `verbose`, then calls `AdminClient.Speedtest`.

Control flow: the legacy admin command only reports deprecation. The support path validates positive duration, object size, and concurrency. It enables autotuning unless the `concurrent` flag was explicitly set, then starts `client.Speedtest` with `madmin.SpeedtestOpts`. JSON mode drains the stream and prints the last versioned result. Interactive mode starts the speed-test UI, forwards every stream result as progress, and finally sends the last result as final.

State and persistence: the server-side speed test may create and clear objects in a bucket, controlled by hidden `bucket` and `noclear` flags. The client itself only forwards results.

Dependencies and integration points: uses MinIO admin speedtest, shared perf conversion/output, `go-humanize` byte parsing, and the speed-test UI.

Risks and test signals: autotune behavior depends on `ctx.IsSet("concurrent")`; hidden bucket/noclear flags can leave server artifacts. Tests should cover parse failures, concurrency validation, JSON final result selection, and error conversion.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf-object.go -->
