<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/top-net-spinner.go -->
# sources/object-store/minio-mc/cmd/top-net-spinner.go

Purpose: provides the Bubble Tea UI model used by `support top net` to render per-interface network throughput.

Important APIs/types/functions: `topNetUI`, `topNetResult`, `GetTotalBytes`, `Update`, `calculationRate`, `View`, and `initTopNetUI`.

Control flow: the UI stores previous/current `topNetResult` samples per endpoint. On each view render, it computes per-second RX/TX rates from counter deltas and sample duration, handles uint64 counter wraparound, sorts endpoints by total throughput, and renders server/interface/receive/transmit rows. Error rows show cross-tick cells and the error string. Quit keys stop the UI.

State and persistence: transient in-memory sample maps and sort flag. No persistence.

Dependencies and integration points: consumed by `support-top-net.go`; depends on Bubble Tea, lipgloss spinner, tablewriter, `madmin.NetMetrics`, Prometheus `procfs.NetDevLine`, humanized byte formatting, and shared UI styles.

Risks and test signals: zero or negative sample durations could divide by zero or produce misleading rates. Tests should cover wraparound, error rendering, missing previous sample, sort order, and quit behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/top-net-spinner.go -->
