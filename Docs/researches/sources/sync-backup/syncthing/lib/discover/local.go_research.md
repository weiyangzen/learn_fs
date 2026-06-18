## sources/sync-backup/syncthing/lib/discover/local.go

Purpose: Implements LAN-local device discovery using IPv4 broadcast or IPv6 multicast beacons.

Important APIs/types/functions: `localClient`, constants `BroadcastInterval`, `CacheLifeTime`, `Magic`, `v13Magic`; `NewLocal`, `Lookup`, `announcementPkt`, `sendLocalAnnouncements`, `recvAnnouncements`, `registerDevice`, `filterUndialableLocal`, and `sanitizeRelayAddresses`.

Control flow: `NewLocal` chooses broadcast for empty host or multicast otherwise, adds beacon, receive, and send services to a supervisor. Sender builds protobuf announcement packets with instance ID and sanitized dialable addresses, then sends on periodic or forced ticks. Receiver validates magic, rejects old/invalid packets, unmarshals announcements, skips self, registers devices, and forces an announcement when a new device appears. Registration reconstructs unspecified advertised addresses from packet source and records cache entries.

State and persistence: Holds local cache, beacon service, per-run random instance ID in sender, broadcast tick channels, and event logger. Cache entries expire after three broadcast intervals.

Dependencies and integration points: Uses generated `discoproto`, beacon package, event `DeviceDiscovered`, address lister from connection service, and protocol device IDs.

Risks: Address filtering/reconstruction must handle IPv4/IPv6 scheme compatibility and avoid leaking relay tokens. `filterUndialableLocal` mutates the input slice in place. Forced broadcast channel is unbuffered and best-effort.

Test signals: `local_test.go` covers instance ID packet changes/new-device detection and undialable address filtering.
