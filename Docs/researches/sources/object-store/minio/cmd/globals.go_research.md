<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/globals.go -->
# sources/object-store/minio/cmd/globals.go

## Purpose
Centralizes process-wide constants, server context, and global subsystem pointers used by MinIO server startup, request handling, storage, security, replication, healing, metrics, and optional protocols.

## Important APIs, types, and functions
- Constants define default ports, modes, owner/storage class defaults, reserved directory suffixes, disk reserve thresholds, memory/request limits, and TLS cache sizing.
- `init` wires `pubsub.GetByteBuffer` to `grid.GetByteBuffer` to avoid circular dependencies.
- `poolDisksLayout`, `disksLayout`, and `serverCtxt` capture parsed server startup configuration, credentials, FTP/SFTP options, memory/network timeouts, and disk layout.
- Global variables hold configuration systems, IAM/policy/lifecycle/bucket metadata systems, event targets, TLS/certs, HTTP server, stats, endpoints/nodes, DNS/etcd, KMS, replication, heal state, forwarders, local drive maps, subnet keys, and service-freeze state.
- Auth plugin accessors/mutators protect plugin pointers with `globalAuthPluginMutex`.
- `errSelfTestFailure` is a startup safety sentinel.

## Control flow
Aside from the `init` hook and plugin getters/setters, this file is declarative global state. Other packages initialize and mutate these globals during startup, config reloads, request handling, healing, and shutdown.

## State and persistence behavior
The file itself persists nothing, but many globals point to persistent subsystems: config, IAM, bucket metadata, lifecycle, KMS, etcd/DNS, replication, tiers, and drive maps. Some values are atomics or mutex-protected; many are conventional package globals that require disciplined initialization order.

## Dependencies and integration points
This is a hub for most MinIO command package integrations: HTTP, console, IAM, policy plugins, storage class, DNS, etcd, KMS, grid, pubsub, certs, drive config, compression, subnet/callhome, replication, healing, and object performance tooling.

## Risks and edge cases
Global mutable state increases test coupling and startup-order sensitivity. Concurrent access must respect documented mutexes or atomics, especially local drive maps, auth plugins, compression config, deployment ID, and service freeze. Adding globals here expands process-wide coupling.

## Test signals
No direct tests in this group. Signals are broad: race tests, startup/shutdown integration tests, config reload tests, plugin set/get behavior, and subsystem initialization failures that expose nil or stale globals.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/globals.go -->
