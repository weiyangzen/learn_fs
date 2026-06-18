<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top-drive.go -->
# sources/object-store/minio-mc/cmd/support-top-drive.go

Purpose: implements `mc support top drive`, showing real-time per-drive IO metrics.

Important APIs/types/functions: `supportTopDriveFlags`, `supportTopDriveCmd`, `checkSupportTopDriveSyntax`, and `mainSupportTopDrive`.

Control flow: the command validates one target, enforces registration, builds an admin client, fetches `ServerInfo` to obtain disk metadata, then starts a Bubble Tea UI from `initTopDriveUI`. A goroutine calls `client.Metrics` with `madmin.MetricsDisk`, one-second interval, `ByDisk=true`, and count `N`; each disk metric is sent as `topDriveResult` to the UI.

State and persistence: read-only; maintains transient previous/current IO counters in the UI.

Dependencies and integration points: integrates with MinIO realtime metrics API, `top-drives-spinner.go` UI code, and support registration.

Risks and test signals: correctness depends on matching disk endpoint keys from `ServerInfo` and metrics. Tests should cover invalid count behavior, server-info failures, metric callback mapping, and UI rate calculations.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top-drive.go -->
