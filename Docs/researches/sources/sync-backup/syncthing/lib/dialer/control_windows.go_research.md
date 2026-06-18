## sources/sync-backup/syncthing/lib/dialer/control_windows.go

Purpose: Windows implementation of reuse-port semantics using `SO_REUSEADDR`.

Important APIs/types/functions: `SupportsReusePort = true`; `ReusePortControl` sets `syscall.SO_REUSEADDR` via `RawConn.Control`.

Control flow: Control hook applies socket option and logs control or socket-option errors before returning them.

State and persistence: Package-level support flag only.

Dependencies and integration points: Used by TCP listener/dialer for port reuse on Windows.

Risks: Windows `SO_REUSEADDR` semantics differ from Unix `SO_REUSEPORT`; behavior is accepted intentionally but can affect binding conflicts.

Test signals: Build-tag compile coverage and Windows network tests elsewhere.
