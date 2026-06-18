## sources/sync-backup/syncthing/lib/nat/structs_test.go

Purpose: tests core `Mapping` helper behavior.

Important tests: `TestMappingValidGateway` checks wildcard, matching IPv4, and mismatching IPv4 gateway behavior. `TestMappingClearAddresses` sets multiple external address entries, subscribes to change notifications, clears addresses, and verifies both notification count and empty external address state.

Control flow and state: tests manipulate `Mapping` internals under the mapping mutex for setup, then call exported methods to assert behavior.

Dependencies and integration points: uses `net.ParseIP` and NAT `Address` values. It validates assumptions used by `Service.acquireNewLocked` and `verifyExistingLocked`.

Risks: does not test ordering, synchronous subscriber blocking, or concurrent access.

Test signals: focused coverage for gateway filtering and address clear notifications.
