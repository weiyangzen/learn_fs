## sources/sync-backup/syncthing/lib/pmp/debug.go

Purpose: registers the NAT-PMP package for debug logging.

Important API: package `init` calls `slogutil.RegisterPackage("NAT-PMP discovery and port mapping")`.

Control flow and state: registration at package initialization.

Dependencies and integration points: enables package-specific logging controls for NAT-PMP discovery and mapping.

Risks: none beyond logging category consistency.

Test signals: no direct tests.
