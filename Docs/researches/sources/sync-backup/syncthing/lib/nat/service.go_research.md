## sources/sync-backup/syncthing/lib/nat/service.go

Purpose: long-running service that discovers NAT/firewall devices and creates or renews external mappings for registered local listener addresses.

Important APIs: `NewService`, `CommitConfiguration`, `Serve`, `NewMapping`, and `RemoveMapping` are the public lifecycle surface. Internal functions `process`, `scheduleProcess`, `updateMapping`, `verifyExistingLocked`, `acquireNewLocked`, `tryNATDevice`, `hash`, and `addrSetsEqual` implement discovery and mapping state transitions.

Control flow and state: the service subscribes to config changes and tracks `enabled`, mappings, and a buffered process trigger under a mutex. `Serve` reacts to timer ticks, scheduled process events, and context cancellation. `process` classifies mappings as due for renewal or waiting, skips discovery when nothing needs renewal, discovers NAT devices, renews expired mappings, and opportunistically updates existing mappings. `updateMapping` sets a new expiry, verifies known NAT devices, acquires missing NAT devices, and notifies subscribers on changes. `tryNATDevice` uses IPv6 pinholes when supported; otherwise it uses deterministic pseudo-random external-port attempts seeded by device ID, local port, and NAT ID, trying requested or generated ports through `AddPortMapping`.

State and persistence: mapping state is in memory only. `Mapping.extAddresses` holds external addresses per NAT device ID; `expires` schedules renewal. On service shutdown, all mapping addresses are cleared and subscribers are notified through `Mapping.clearAddresses`; the code does not explicitly delete mappings from gateways, matching `RemoveMapping` semantics.

Dependencies and integration points: depends on `config.Wrapper` NAT options (`NATEnabled`, renewal, timeout, lease), protocol device ID for deterministic port selection, registered NAT providers, and `Mapping` notifications used by discovery/announcement code.

Risks: renewal timing depends on config values; zero renewal falls back to 30 minutes for scheduling but discovery still receives the configured renewal duration. The mapping mutex is held while calling NAT devices, which can block address readers/subscribers if devices hang despite contexts. External port selection is deterministic, useful for stability but can collide. `RemoveMapping` does not remove gateway mappings, so stale leases rely on expiry.

Test signals: no direct service test here. `structs_test.go` covers `Mapping` address/gateway helpers used by the service.
