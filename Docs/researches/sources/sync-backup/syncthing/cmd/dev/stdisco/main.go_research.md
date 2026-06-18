# sources/sync-backup/syncthing/cmd/dev/stdisco/main.go

Purpose: development utility for observing and optionally stimulating Syncthing local discovery announcements over multicast and broadcast beacons.

Important APIs/types/functions: flags `-all`, `-fake`, `-mc`, and `-bc`; globals `randomPrefix` and `myID`; functions `runbeacon`, `recv`, `send`, and `randomDeviceID`. It uses `beacon.Interface`, `discoproto.Announce`, `discover.Magic`, and `protocol.DeviceID`.

Control flow: `main` starts multicast and broadcast beacon servers, starts receive loops for both, and optionally starts fake announcement senders. `recv` validates magic, unmarshals protobuf announcements, filters its own fake ID, suppresses duplicate device/source pairs unless `-all`, and logs device addresses. `send` emits a fake announce every second.

State and persistence behavior: no persistence. Runtime state includes a seen map per receiver and generated fake device ID.

Dependencies/integration: integrates with Syncthing beacon/discovery/protocol libraries and protobuf-generated discovery messages.

Risks/test signals: malformed packets can be dropped silently after unchecked protobuf unmarshal errors. Infinite goroutines run until process exit. Signal is visible announcement logs or fake probes causing peers to respond.
