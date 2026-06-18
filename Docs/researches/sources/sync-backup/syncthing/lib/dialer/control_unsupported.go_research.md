## sources/sync-backup/syncthing/lib/dialer/control_unsupported.go

Purpose: Solaris fallback for reuse-port support.

Important APIs/types/functions: `SupportsReusePort = false`; `ReusePortControl` returns nil.

Control flow: Always disables port reuse and allows callers to proceed without special socket options.

State and persistence: Constant package-level state.

Dependencies and integration points: Satisfies the same API used by TCP listener/dialer on unsupported platforms.

Risks: NAT punch-through quality may be lower on this platform, but correctness is maintained.

Test signals: Build-tag compile coverage only.
