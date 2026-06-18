# sources/sync-backup/syncthing/lib/connections/lan_test.go

## sources/sync-backup/syncthing/lib/connections/lan_test.go

Purpose: Tests LAN host classification with loopback, configured local networks, public addresses, and invalid host strings.

Important APIs/types/functions: `TestIsLANHost` constructs a config wrapper with `Options.AlwaysLocalNets` and calls `lanChecker.isLANHost`.

Control flow and state: The cases verify loopback is LAN, `10.20.30.0/24` is LAN due to config, `192.0.2.1` is not LAN, and malformed host strings return false rather than erroring outward.

Dependencies and integration: Uses `config.Wrap`, `events.NoopLogger`, `protocol.LocalDeviceID`, and `lanChecker` from connection service code.

Risks and test signals: LAN classification controls bandwidth-limit behavior, local address announcement, and connection prioritization. The test guards both configured networks and robust parsing.
