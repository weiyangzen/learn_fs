# sources/object-store/minio/cmd/update-notifier.go

Purpose: formats the server update notification shown when a newer MinIO release is available.

Important APIs and functions: `prepareUpdateMessage(downloadURL string, older time.Duration) string` decides whether to return a message and selects JSON/plain formatting. `colorizeUpdateMessage(updateString, newerThan string) string` builds a terminal-friendly boxed notification.

Control flow: `prepareUpdateMessage` returns empty when no download URL is available or `older <= 0`. It uses `humanize.RelTime` to express how far behind the current release is. In JSON mode (`globalServerCtxt.JSON`) it returns a plain sentence with the update URL. Otherwise it delegates to `colorizeUpdateMessage`. The colorized path computes visible line widths without ANSI escapes, checks terminal width with `pb.GetTerminalWidth`, falls back to plain lines if too narrow, and uses Unicode box drawing except on Windows, where ASCII borders are used.

State and persistence: no persistence. It reads global server context and runtime OS, and produces display strings.

Dependencies and integration points: depends on `go-humanize`, `cheggaaa/pb` terminal-width detection, MinIO color helpers, `runtime.GOOS`, and `globalWindowsOSName`. It integrates with startup/update-check logging paths.

Risks: terminal-width and ANSI handling can regress layout; width calculations are byte-length based, which is acceptable for the current English templates but would be fragile for wide characters. JSON mode deliberately avoids color/box formatting so machine-readable logs remain simple.

Test signals: no local tests. Useful tests would assert empty cases, JSON message format, narrow-terminal fallback, and Windows ASCII border selection.
