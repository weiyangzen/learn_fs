<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top-rpc.go -->
# sources/object-store/minio-mc/cmd/support-top-rpc.go

Purpose: implements `mc support top rpc`, a real-time or replayable terminal UI for MinIO grid/RPC metrics.

Important APIs/types/functions: `supportTopRPCFlags`, `supportTopRPCCmd`, `checkSupportTopRPCSyntax`, `mainSupportTopRPC`, `topRPCUI`, `Update`, `View`, and `initTopRPCUI`. Sort constants define sort modes for host, reconnections, queue, and ping.

Control flow: if `--in` is provided, no target is required; the command opens a JSON-lines file, optionally wraps it in zstd decompression for `.zst`, replays `madmin.RealtimeMetrics` frames preserving capped inter-frame delay, and exits. Live mode validates target, enforces registration, creates an admin client, and streams `madmin.MetricsRPC` with interval, count, host filters, and `ByHost=true`. JSON mode prints raw metrics; interactive mode sends each metrics frame into `topRPCUI`.

State and persistence: read-only live mode; replay mode reads local files. UI state includes current/frozen metrics, offset, page size, direction toggle, and sort mode.

Dependencies and integration points: uses MinIO realtime metrics, Bubble Tea, lipgloss spinner, zstd, tablewriter, support registration, and global terminal sizing.

Risks and test signals: replay mode calls `os.Exit(0)` from a goroutine, which complicates tests and cleanup. Tests should cover `--in` parsing, zstd replay, host filters, JSON mode, freeze/toggle/sort keys, and nil RPC metrics rendering.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top-rpc.go -->
