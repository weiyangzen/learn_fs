<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/config.rs -->
# sources/object-store/garage/src/util/config.rs

## Purpose
TOML configuration schema and deserialization helpers for a Garage node, covering storage paths, replication/consistency, RPC, discovery, metadata database, S3/K2V/web/admin APIs, compression, buffering, and feature toggles.

## Important APIs, types, and functions
Primary type is `Config`, with nested `DataDirEnum`, `DataDir`, `S3ApiConfig`, `K2VApiConfig`, `WebConfig`, `AdminConfig`, `ConsulDiscoveryAPI`, `ConsulDiscoveryConfig`, and `KubernetesDiscoveryConfig`. `read_config` parses a file. Helpers provide defaults and custom deserializers for compression and byte capacities.

## Control flow
Serde deserializes TOML into the typed schema, applying defaults and custom visitors. Compression accepts integer levels or string `none`; capacity fields accept integers or strings parsed by `bytesize`. The test writes a minimal config and verifies `rpc_secret` parsing.

## State and persistence behavior
This module reads configuration from disk but does not mutate it. Parsed values drive persistent storage locations, fsync behavior, data directory capacity/read-only semantics, metadata snapshots, RPC secrets, and admin tokens.

## Dependencies and integration points
Consumed by Garage startup, API servers, discovery code, DB initialization, block manager, and admin/metrics/tracing setup. Depends on serde, TOML, bytesize, socket address parsing, and Garage error handling.

## Risks and test signals
Misparsed capacity/compression values can cause memory pressure or disabled compression unexpectedly. Optional secret-file fields require external permission checks elsewhere. Tests should cover both single/multiple data dirs, Unix/TCP API addresses, invalid capacities, compression `none`, and default consistency/database values.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/config.rs -->
