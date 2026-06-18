## sources/sync-backup/syncthing/lib/nat/registry.go

Purpose: global registry for NAT discovery providers and concurrent discovery fan-out.

Important APIs: `DiscoverFunc` is the provider signature. `Register` appends a provider to the global list. `discoverAll` runs all providers concurrently and returns a map from device ID to discovered `Device`.

Control flow and state: `discoverAll` starts one goroutine per provider, streams discovered devices through a channel, and uses a collector goroutine to fill the result map until all providers finish or context is canceled. Duplicate IDs are overwritten by the last received device.

Dependencies and integration points: providers register in package `init` functions such as `pmp.init`. `nat.Service.process` calls `discoverAll` before mapping renewal/acquisition.

Risks: `providers` is a package-level slice with no registration lock; registration is expected during init. Provider functions must respect context or discovery can block service processing. Duplicate provider IDs are silently overwritten.

Test signals: no direct tests in this subset.
