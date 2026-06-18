# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/connection.c

This file manages configured active and passive IPsec/IKE connections.

Key responsibilities:
- Initializes active connections from the `Phase 2` `Connections` list.
- Records passive connections from active connections not marked `active-only` and from `Passive-Connections`.
- Schedules recurring checks for required active connections.
- Matches incoming passive exchanges by local/remote ISAKMP IDs.
- Tears down and rebuilds connection state during reinitialization.
- Reports active and passive connection state.

Important structures:
- `struct connection`: active connection name and timer event.
- `struct connection_passive`: passive connection name plus encoded local/remote IDs and lengths.
- Global TAILQs `connections` and `connections_passive`.

Important functions:
- `connection_init()`: populates active and passive connection lists from config.
- `connection_setup()`: adds an active connection and schedules an immediate checker event.
- `connection_checker()`: reschedules itself and calls `pf_key_v2_connection_check`.
- `connection_record_passive()`: builds and stores local/remote IDs for passive matching.
- `connection_passive_lookup_by_ids()`: finds passive config by comparing peer IDs, including a local-ID-only road-warrior fallback.
- `connection_teardown()` and `connection_passive_teardown()` remove entries.
- `connection_reinit()` clears and rebuilds connection lists.
- `connection_report()` logs current connection state.

Dependencies:
- Config service from `conf.h`.
- IPsec DOI ID construction via `ipsec_build_id`.
- PF_KEY v2 checking via `pf_key_v2_connection_check`.
- Timer and UI state.
- DOI lookup for report-time ID decoding.

Research notes:
- This module ties persistent configuration to daemon liveness behavior: active connections are periodically rechecked, while passive connections are used to select config for inbound exchanges.
