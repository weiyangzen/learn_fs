# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/logging/logging.go

Purpose: logrus logger initialization and file lifecycle helpers for KCS/LTM.

Important APIs: constants define `/var/log/go/`, `server.log`, `ltm_logs/`, `kcs_logs/`, and cache log dir. Flags `DEBUG` and `MOCK` are compile-time constants. Functions `InitLogger`, `CloseLog`, `Sync`, and `GetFile` create file-backed debug loggers, close/sync file outputs, and expose the underlying file.

State and dependencies: appends to log files with mode 0644; falls back to stdout if the file cannot be opened; uses logrus text formatter and caller reporting.

Integration points: every server, sharder, watcher, bisector, build, and failure email path uses this package.

Risks and test signals: `InitLogger("")` falls back to stdout, used by mock code. Caller reporting can be expensive. `GetFile` returns nil for non-file outputs, requiring callers to check before dereferencing; `email.ReportFailure` currently assumes non-nil. Tests should cover fallback behavior and close/sync no-ops.
