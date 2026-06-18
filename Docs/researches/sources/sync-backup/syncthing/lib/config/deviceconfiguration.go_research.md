# sources/sync-backup/syncthing/lib/config/deviceconfiguration.go

## sources/sync-backup/syncthing/lib/config/deviceconfiguration.go

Purpose: Defines per-remote-device configuration and preparation logic.

Important APIs/types/functions: `DeviceConfiguration` includes identity, addresses, compression, introducer flags, bandwidth limits, ignored folders, request limits, untrusted mode, GUI port, connection count, and group. Methods/functions include `Copy`, `prepare`, `NumConnections`, `IgnoredFolder`, `Description`, and observed-folder dedup/sorting helpers.

Control flow and state: `prepare` normalizes empty addresses to `dynamic`, deduplicates ignored folders by newest timestamp, removes ignored folders that are now shared, and disallows untrusted devices from being introducers or auto-accepting folders. `NumConnections` maps zero to the package default of three, negative to one, and positive to itself.

Dependencies and integration: Depends on `protocol.DeviceID`, sorting, and structured logging. `Configuration.prepareDevices` supplies shared folder IDs so device ignored-folder state remains consistent with folder sharing.

Risks and test signals: Untrusted-device flag interactions are security-sensitive because they prevent trusted sharing and auto-accept behavior. Tests cover dynamic address defaults, ignored folder pruning, duplicate observed folders indirectly, and untrusted introducer sanitization.
