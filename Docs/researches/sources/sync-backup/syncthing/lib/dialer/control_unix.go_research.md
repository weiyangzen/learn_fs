## sources/sync-backup/syncthing/lib/dialer/control_unix.go

Purpose: Detects and applies `SO_REUSEPORT` on Unix-like systems excluding Solaris and Windows.

Important APIs/types/functions: Package variable `SupportsReusePort`; `init` probes socket option support; `ReusePortControl` is a `net.ListenConfig`/`net.Dialer` control hook.

Control flow: Init creates an IPv4 TCP socket, attempts `unix.SetsockoptInt(SO_REUSEPORT)`, logs support, and flips `SupportsReusePort`. Control hook no-ops if unsupported; otherwise calls `RawConn.Control` to set the option.

State and persistence: Process-global boolean only.

Dependencies and integration points: Used by TCP listener and registry-aware TCP dialer to improve NAT punch-through and stable ports.

Risks: Probe behavior varies by OS/kernel. Control hook must not fail on unsupported systems because listener startup depends on it.

Test signals: No direct tests; platform-specific build and runtime networking exercise this path.
