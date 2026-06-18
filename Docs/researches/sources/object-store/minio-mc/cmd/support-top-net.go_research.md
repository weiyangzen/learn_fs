<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top-net.go -->
# sources/object-store/minio-mc/cmd/support-top-net.go

Purpose: implements `mc support top net`, a real-time view of network metrics per host/interface.

Important APIs/types/functions: `supportTopNetFlags`, `supportTopNetCmd`, `checkSupportTopNetSyntax`, and `mainSupportTopNet`.

Control flow: after syntax and registration checks, the command creates an admin client and constructs `madmin.MetricsOptions` with `MetricNet`, configurable interval/count, and `ByHost=true`. JSON mode prints every `RealtimeMetrics` callback as `metricsMessage`. Interactive mode starts `initTopNetUI`, maps each host's `Net` metrics into `topNetResult`, forwards first host errors if present, and quits when the metrics call ends.

State and persistence: read-only; UI keeps previous/current samples to compute rates.

Dependencies and integration points: depends on MinIO realtime metrics API, `top-net-spinner.go`, shared metrics JSON message type, support registration, and global JSON mode.

Risks and test signals: interval values are not explicitly validated for positivity. Tests should cover JSON streaming, context cancellation, host error forwarding, and rate calculation for counter wraparound in the UI.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top-net.go -->
