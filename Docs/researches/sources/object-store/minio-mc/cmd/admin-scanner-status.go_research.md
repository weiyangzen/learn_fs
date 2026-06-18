# sources/object-store/minio-mc/cmd/admin-scanner-status.go

## Purpose
Implements `mc admin scanner status`/`info`, displaying scanner activity, bucket scan history, live metrics, or replayed saved metrics.

## Important APIs, types, and functions
Important symbols are `adminScannerInfoFlags`, `adminScannerInfo`, `checkAdminScannerInfoSyntax`, `bucketScanMsg`, `mainAdminScannerInfo`, `metricsMessage`, `initScannerMetricsUI`, `scannerMetricsUI`, `metricsDuration`, `metricsUint64`, and `metricsTitle`.

## Control flow
The handler validates either an input replay file or one target alias. Replay mode opens plain or `.zst` JSON lines, sleeps according to recorded collection time, and sends scanner metrics into the UI. Live mode creates an admin client, optionally fetches `BucketScanInfo`, otherwise streams `madmin.MetricsScanner` with node, count, interval, and path-display options. JSON mode prints each metrics snapshot; interactive mode runs Bubble Tea.

## State and persistence behavior
The command is read-only. It observes server scanner metrics and bucket scan timestamps. Local UI state stores the current metrics snapshot, spinner, quit flag, and max path count.

## Dependencies and integration points
It integrates realtime metrics APIs, bucket scan info APIs, Bubble Tea, spinner/lipgloss, zstd replay, tablewriter, humanize, global terminal dimensions, and shared `metricsMessage` used by resync status.

## Risks and edge cases
Replay mode calls `os.Exit(0)` after playback, bypassing normal returns. Rate calculation uses a fixed minute denominator in `getRate`, which should be checked. Active path output is clipped by terminal size and `max-paths`.

## Test signals
Tests should cover syntax for live and replay modes, zstd replay decoding, bucket scan full-scan detection, JSON metrics output, UI quit/final handling, max-path clipping, no-data view, and metrics formatting helpers.
