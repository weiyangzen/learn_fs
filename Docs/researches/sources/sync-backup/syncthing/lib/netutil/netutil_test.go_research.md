## sources/sync-backup/syncthing/lib/netutil/netutil_test.go

Purpose: validates `AddressURL` formatting.

Important test: `TestAddress` checks several network/host combinations such as `tcp` and arbitrary strings, expecting `scheme://host`.

Control flow and state: table-driven, stateless.

Dependencies and integration points: exercises only local string construction, not gateway discovery.

Risks: no tests for IPv6 host formatting, empty values, escaping, or fallback gateway behavior.

Test signals: narrow smoke coverage for URL construction.
