# sources/sync-backup/syncthing/lib/config/optionsconfiguration.go

## sources/sync-backup/syncthing/lib/config/optionsconfiguration.go

Purpose: Defines global Syncthing options and helper methods for defaults, normalization, derived network settings, concurrency limits, upgrade/reporting flags, and connection priorities.

Important APIs/types/functions: `OptionsConfiguration` includes listen/discovery/STUN settings, local/global announce flags, bandwidth limits, NAT/relay settings, usage/crash reporting, upgrades, temp/cache/progress settings, LAN-local nets, low priority, folder concurrency, request limits, feature flags, audit fields, connection limits, and connection priority fields. Methods include `Copy`, `prepare`, `RequiresRestartOnly`, `IsStunDisabled`, `ListenAddresses`, `StunServers`, `GlobalDiscoveryServers`, `MaxFolderConcurrency`, `MaxConcurrentIncomingRequestKiB`, `AutoUpgradeEnabled`, `FeatureFlag`, and `LowestConnectionLimit`.

Control flow and state: `prepare` fills nil slices, unique-trims listen and discovery servers, clamps reconnect interval to at least five seconds, removes the auth notification once GUI user/password is set, clamps negative connection limits to zero, keeps WAN priorities above LAN priorities, and generates a usage-reporting unique ID when needed. Derived address methods expand `"default"` placeholders into package defaults; STUN resolution performs DNS SRV lookup and appends shuffled fallback servers.

Dependencies and integration: Uses `runtime.GOMAXPROCS`, DNS, `protocol.MaxBlockSize`, `rand`, `stringutil`, and `structutil`. Connection services consume listen addresses, discovery, relays, bandwidth, LAN limit flags, connection limits, and priorities.

Risks and test signals: Network defaults and derived values affect reachability. DNS lookup in `StunServers` can vary at runtime. Tests cover overridden option values, max folder concurrency, migration interactions, and address/default behavior through fixtures.
