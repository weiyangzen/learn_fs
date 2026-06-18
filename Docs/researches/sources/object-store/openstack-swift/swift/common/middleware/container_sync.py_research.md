# sources/object-store/openstack-swift/swift/common/middleware/container_sync.py

## Purpose
`container_sync.py` validates incoming container-sync requests that use Swift realm/cluster configuration. It also validates `X-Container-Sync-To` metadata updates and advertises configured realms through `/info`.

## Important APIs, Types, and Functions
`ContainerSync` owns a `ContainerSyncRealms` instance, configuration flags, current realm/cluster info, and WSGI request handling. `register_info()` publishes available realms/clusters and marks the current cluster when configured. `filter_factory()` builds the middleware.

## Control Flow
Initialization loads `container-sync-realms.conf` from `swift_dir`, parses `allow_full_urls`, parses `current`, and registers info. `/info` requests refresh registration before pass-through. Swift API requests fetch container info with `swift_source='CS'`. Container `PUT`/`POST` requests are rejected if they attempt to configure sync on a versioned container. If full URLs are disabled, non-realm `X-Container-Sync-To` values are rejected. Requests with `X-Container-Sync-Auth` are split into realm, nonce, and signature; signatures are checked with primary and secondary realm keys plus the container sync key. Valid sync requests set authorize, SLO, and symlink override flags.

## State and Persistence
Persistent data lives in `container-sync-realms.conf` and container metadata such as sync key and sync destination. The middleware stores current config in memory and appends log-info markers to the request environ.

## Dependencies and Integration Points
It depends on realm configuration, `get_container_info`, constant-time signature comparison, `append_log_info`, Swift API-version parsing, and `/info` registry. It integrates with gatekeeper via `x-backend-inbound-x-timestamp`, with auth via `swift.authorize_override`, and with SLO/symlink middleware via override flags.

## Risks and Edge Cases
Bad realm config or current cluster naming only logs errors but may affect `/info`. Missing local realm key, missing user sync key, malformed auth header, or invalid signature all deny with a SwiftContainerSync authenticate challenge. Clock/timestamp behavior depends on upstream sync clients. Enabling full URL sync destinations widens the configuration surface.

## Test Signals
Tests should cover `/info` refresh, realm/cluster publication, invalid `current`, versioning conflict rejection, full-url disabled validation, valid and invalid sync auth signatures, key2 rotation, timestamp shunting from gatekeeper, authorize/SLO/symlink override flags, and log-info markers for failure causes.
