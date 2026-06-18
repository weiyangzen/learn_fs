# sources/object-store/minio/cmd/config-current.go

## Purpose
`config-current.go` registers current configuration defaults/help, validates subsystem configuration, looks up persisted/env-overridden values, applies dynamic settings to global runtime systems, and loads/saves the current `config.Config`.

## Important APIs, Types, And Functions
`initHelp` registers default KVS and help for site, API, scanner, batch, identity, policy, logger/audit, notifications, lambda, SUBNET/callhome, drive, browser, ILM, and erasure-only storage/heal subsystems. `globalServerConfig` plus `globalServerConfigMu` hold process config. `validateSubSysConfig` and `validateConfig` validate a target subsystem, including live connection checks for etcd/LDAP and callhome license gating. `lookupConfigs` initializes DNS/etcd/site/encryption/notification/lambda and calls `applyDynamicConfig`. `applyDynamicConfigForSubSys` updates global API, compression, heal, batch, scanner, logger/audit, storage class, SUBNET, callhome, drive, browser, and ILM state. `GetHelp`, `newSrvConfig`, `getValidConfig`, and `loadConfig` expose help and config load/save flows.

## Control Flow
Defaults and help are registered once. Validation disables env merging under `env.LockSetEnv` to test persisted config alone, then validates one subsystem or all. Loading reads server config, overlays env-derived runtime settings in `lookupConfigs`, and swaps `globalServerConfig` under lock. Dynamic apply iterates `config.SubSystemsDynamic`; callhome startup is triggered when config changes from disabled to enabled.

## State And Persistence Behavior
The file mutates many global runtime systems but persists only through `saveServerConfig` in other files. It updates scanner atomics, logger targets, remote transports, worker counts, SUBNET env exports, and the in-memory server config map.

## Dependencies And Integration Points
It is a central integration point for MinIO's internal config packages, object layer drive counts, global root CAs, IAM identity config, notification/lambda target creation, logger target updates, scanner throttling, lifecycle workers, and callhome.

## Risks And Test Signals
Risks include global mutable state, partial dynamic-apply failures, live external validation causing startup/admin-set failures, and environment merging needing strict locking. `config-current_test.go` verifies region initialization and update lookup. Most subsystem behavior relies on package-specific tests and integration tests.
