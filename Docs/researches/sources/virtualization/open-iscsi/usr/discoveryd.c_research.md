# File Research: sources/virtualization/open-iscsi/usr/discoveryd.c

Implements the discovery daemon helper logic. It forks discovery/login workers, periodically refreshes target lists, reconciles sessions, and optionally handles iSNS SCN registration/notification.

Core behavior:
- Global `iscsi_targets` stores target portals currently managed by discoveryd.
- `update_sessions` compares new discovery results against current targets, logs into new portals asynchronously, and logs out stale portals.
- `fork_disc` starts a child helper and registers it for shutdown/reaping.
- SendTargets discovery loops at configured poll intervals, binds ifaces to discovered nodes, then updates sessions.
- `discoveryd_start` starts configured iSNS and SendTargets discovery records from idbm.

iSNS-specific behavior:
- Builds initiator/entity/portal objects for registration.
- Registers for SCNs when supported and requested.
- Falls back to polling/DevAttrQuery refresh depending on configuration and server behavior.
- Maintains registration refresh timers using server registration period or configured poll interval.
- Handles SCN callbacks by querying changed target portals and updating sessions.

Shutdown:
- `SIGTERM` sets `stop_discoveryd`.
- On stop, managed sessions may be logged out and target records freed.
- Child helpers are tracked via `event_poll` reaping and shutdown callbacks.
