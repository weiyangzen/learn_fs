# sources/storage-engines/foundationdb/fdbclient/GlobalConfig.cpp

## Purpose
`GlobalConfig.cpp` maintains the client-side global configuration cache and provides the transaction helper used to mutate global configuration keys. It stores config under the system key prefix, records version-stamped mutation history, refreshes from GRV proxies, applies incremental history from `ClientDBInfo`, and notifies watchers/callbacks.

## Important APIs, Types, And Functions
The file defines well-known global config keys for client transaction sampling and visibility sampling. `GlobalConfig::applyChanges()` writes user-visible config keys, records `VersionHistory`, and bumps `globalConfigVersionKey`. Cache APIs include `prefixedKey()`, `get(KeyRef)`, `get(KeyRangeRef)`, `onInitialized()`, `onChange()`, `trigger()`, `insert()`, and `erase()`. Actor methods `refresh()` and `updater()` populate and maintain the cache.

## Control Flow
`applyChanges()` converts insertions and clears to both transaction mutations and serialized `VersionHistory`, then uses versionstamped atomic ops to make the change discoverable. `refresh()` clears local cache, calls a GRV proxy `refreshGlobalConfig` request through load balancing with timeout/backoff, inserts returned config after removing `globalConfigKeysPrefix`, and optionally waits until a requested largest-seen version is reached. `updater()` waits for database connection, performs the initial full refresh, fulfills `initialized`, then loops on `dbInfoChanged`: if history is too old it refreshes fully, otherwise it applies `SetValue` and `ClearRange` mutations in ascending version order and triggers `configChanged`.

## State And Persistence Behavior
Persistent FoundationDB state is under `globalConfigKeysPrefix`, `globalConfigHistoryPrefix`, and `globalConfigVersionKey`. Local process state is `data`, `lastUpdate`, callback registrations, and initialization/change triggers. Values are tuple-decoded into `std::any` variants for strings, integers, booleans, floats, doubles, and versionstamps. Erases call registered callbacks with `std::nullopt`.

## Dependencies And Integration Points
The implementation depends on `DatabaseContext`, `GlobalConfig.h`, `SpecialKeySpace`, `SystemData`, tuple encoding, `ObjectWriter`, `GrvProxyInterface::refreshGlobalConfig`, load balancing, Flow actors, `Backoff`, and client knobs for refresh timing. Cluster controllers and proxies consume the history/version keys to distribute updates to clients.

## Risks And Edge Cases
`insert()` assumes the tuple has at least one supported element and asserts on unsupported types; malformed tuples only produce a warning. `refresh()` erases the whole local cache before it succeeds, so callbacks may see transient removals only through later `erase()` paths, not during initial erase-all. History gaps require full refresh; if `dbInfo->history` mutates while waiting, the loop deliberately rechecks. Callback lookup uses copied/stable keys, so arena lifetime must remain tied to `ConfigValue`.

## Test Signals
Expected coverage includes special-key-space configuration writes, versionstamp history entries, initial `onInitialized()` behavior, callback invocation on insert/clear, full-refresh after history gaps, tuple parse warnings, and clients observing changes after `globalConfigVersionKey` updates.
