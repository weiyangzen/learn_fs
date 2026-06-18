<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/default_storage.go -->
# sources/user-network-fs/rclone/fs/config/default_storage.go

## Purpose
Provides `defaultStorage`, an in-memory implementation of the config `Storage` interface used when configuration is not backed by an on-disk config file or when tests need ephemeral storage.

## Important APIs, Types, And Control Flow
`defaultStorage` is a mutex-protected `map[section]map[key]value`. It implements section discovery, section existence/deletion, key listing, value get/set/delete, no-op `Load` and `Save`, and JSON `Serialize`. `SetValue` lazily creates missing sections; delete methods are idempotent where possible.

## State And Persistence
All state lives in memory and is guarded by an RWMutex. `Load` and `Save` deliberately do no persistence; `Serialize` emits a JSON snapshot of the map rather than rclone's normal config-file syntax.

## Dependencies And Integration Points
Only depends on `encoding/json` and `sync`. The compile-time `var _ Storage` check ties it to the wider config storage abstraction.

## Risks And Test Signals
The JSON serialization differs from file-backed INI serialization, so callers must not rely on it for encrypted or configfile-compatible output. Tests cover section/key CRUD and serialization success, but not concurrent access.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/default_storage.go -->
