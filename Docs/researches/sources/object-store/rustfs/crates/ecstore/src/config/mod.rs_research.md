# sources/object-store/rustfs/crates/ecstore/src/config/mod.rs

## Purpose
This module wires ecstore configuration submodules into startup initialization. It registers default KVS for storage class, scanner, heal, notify, audit, and OIDC; loads persisted server config; applies dynamic lookup; and exposes storage-class globals.

## Important APIs, types, and functions
Exports include `GLOBAL_STORAGE_CLASS`, `GLOBAL_CONFIG_SYS`, `RUSTFS_CONFIG_PREFIX`, `ConfigSys`, `get_global_storage_class`, `set_global_storage_class`, `init_global_config_sys`, `try_migrate_server_config`, and `init`. It publicly exposes `com`, `heal`, and `storageclass`.

## Control flow
`init` builds a subsystem-to-default-KVS map and calls `register_default_kvs`. `init_global_config_sys` calls `ConfigSys::init`, which reads config through `read_config_without_migrate`, calls `lookup_configs`, and installs the result with `set_global_server_config`. Migration is a separate explicit call to `com::try_migrate_server_config`.

## State and persistence behavior
The module persists nothing directly. It coordinates global server config in `rustfs_config::server_config` and storage-class runtime state in `GLOBAL_STORAGE_CLASS`. Storage-class set/get silently skip or return `None` on lock failure.

## Dependencies and integration points
It depends on `ECStore`, sibling default modules, and `rustfs_config` subsystem constants. Object placement and inlining depend on the storage-class global this module exposes.

## Risks and edge cases
Idempotency depends on `register_default_kvs` behavior. Silent lock failures can hide poisoned storage-class state. Private notify/audit/OIDC/scanner modules force callers through central registration, so missing registration breaks admin visibility.

## Test signals
Tests verify storage-class global server-config round trip and scanner/heal default registration. They do not run full object-store initialization or validate every default subsystem.
