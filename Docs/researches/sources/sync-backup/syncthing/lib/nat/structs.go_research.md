## sources/sync-backup/syncthing/lib/nat/structs.go

Purpose: data structures representing a requested local mapping and externally visible addresses assigned by NAT devices.

Important types/functions: `MappingChangeSubscriber`, `Mapping`, and `Address`. `Mapping` methods include `setAddressLocked`, `removeAddressLocked`, `clearAddresses`, `notify`, `Protocol`, `Address`, `ExternalAddresses`, `OnChanged`, `String`, `GoString`, and `validGateway`. `Address` provides `Equal`, `String`, and `GoString`.

Control flow and state: `Mapping` stores requested protocol/local address, IP version, a per-device map of external addresses, expiry time, and change subscribers under an RW mutex. Address setters/removers require the caller to hold the write lock and then call `notify` outside service-level decisions. `ExternalAddresses` flattens all per-device address slices. `clearAddresses` drops all external addresses and notifies. `validGateway` allows wildcard local IPs or exact local gateway IP matches.

Dependencies and integration points: used by `Service` to expose mapping results and by discovery/announcement code to subscribe to changes. Address formatting relies on `net.JoinHostPort`.

Risks: subscriber callbacks run synchronously in `notify`; a slow or reentrant subscriber can block NAT processing. `ExternalAddresses` order is map-dependent. Callers must respect lock expectations for `setAddressLocked`/`removeAddressLocked`.

Test signals: `structs_test.go` covers gateway matching and clearing addresses.
