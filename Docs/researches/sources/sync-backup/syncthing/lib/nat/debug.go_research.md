## sources/sync-backup/syncthing/lib/nat/debug.go

Purpose: defines the package-level logging adapter for NAT discovery and port mapping.

Important API: variable `l = slogutil.NewAdapter("NAT discovery and port mapping")` is used by NAT service code for debug logging.

Control flow and state: no runtime control flow beyond package initialization.

Dependencies and integration points: depends on `internal/slogutil`; used by `service.go` for debug traces around discovery, renewals, and mapping attempts.

Risks: none beyond logging category naming consistency.

Test signals: no direct tests; logging adapter behavior is covered elsewhere.
