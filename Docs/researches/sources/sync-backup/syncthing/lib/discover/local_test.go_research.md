## sources/sync-backup/syncthing/lib/discover/local_test.go

Purpose: Tests local discovery instance ID semantics and local address filtering.

Important APIs/types/functions: `TestLocalInstanceID`, `TestLocalInstanceIDShouldTriggerNew`, `padDeviceID`, and `TestFilterUndialable`.

Control flow: Tests create local clients, generate announcements with different instance IDs, register synthetic device announcements from a UDP source, and compare new-device boolean outcomes. Filtering test feeds valid and invalid TCP/QUIC URLs and compares retained list.

State and persistence: In-memory local client/cache only.

Dependencies and integration points: Uses generated discovery proto, protocol IDs, fake address lister, and events noop logger.

Risks: Tests do not fully exercise beacon send/receive network I/O. Filtering assertions depend on current `net.ResolveTCPAddr` behavior.

Test signals: Good coverage for cache newness trigger and address safety filtering.
