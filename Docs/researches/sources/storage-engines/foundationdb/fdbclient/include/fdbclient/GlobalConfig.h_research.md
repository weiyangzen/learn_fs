# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/GlobalConfig.h

Purpose: Declares the eventually consistent global configuration framework used to synchronize small typed key-value pairs to clients and servers through database history and GRV proxy refreshes.

Important APIs/types/functions: `VersionHistory` stores a version and mutations for global config history. Extern keys include client transaction sample rate/size limit, transaction tag sampling rate/cost, and sampling frequency/window. `ConfigValue` owns an arena plus `std::any` decoded value. `GlobalConfig` constructs with `DatabaseContext*`, initializes against an `AsyncVar<ClientDBInfo>`, applies transactional changes with `applyChanges()`, prefixes keys with the global config system prefix, reads single/range values, returns arithmetic defaults, exposes `onInitialized()` and `onChange()`, and registers per-key callbacks with `trigger()`.

Control flow: `init()` starts an updater actor and forwards client-info changes to an internal trigger. The updater uses `ClientDBInfo::history` and/or `refresh()` to update the local key-value map. Local `insert()`/`erase()` mutate in-memory config and trigger callbacks; persistent writes must be done by applying mutations to a transaction through `applyChanges()`.

State and persistence behavior: Persistent state lives under `\xff\xff/global_config/<key>` encoded with FDB tuple typecodes. Local state is an unordered map from string refs to `ConfigValue` references, last update version, initialization promise, change trigger, and callbacks. Values containing allocated objects rely on `ConfigValue` arenas for lifetime.

Dependencies and integration points: Depends on commit mutations, FDB types, Flow actors, `DatabaseContext`, `ClientDBInfo`, and `Transaction`. Integrated with GRV proxy `GlobalConfigRefreshRequest/Reply`, `ClientDBInfo::history`, `DatabaseContext::globalConfig`, and sampling/throttling knobs.

Risks: `trigger()` requires keys to be global config string literals to guarantee memory validity. `std::any` casts can fail if decode/type assumptions drift. Large values or too many keys can slow synchronization. Persistent writes that bypass tuple encoding cannot be decoded correctly.

Test signals: Applying insert/clear mutations to transactions; prefix generation; local refresh from version history and full range refresh; callback invocation on set/clear; arithmetic default reads; arena lifetime for object values; GRV proxy refresh integration; initialization/onChange futures.
