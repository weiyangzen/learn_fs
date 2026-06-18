# sources/storage-engines/foundationdb/fdbcli/RangeConfigCommand.cpp

Purpose: Implements `rangeconfig`, exposing per-key-range data distribution configuration hints such as replication factor and team ID.

Important APIs/types/functions: `rangeConfigCommandActor(Database, tokens)`, `rangeConfigGenerator`, `DDConfiguration().userRangeConfig()`, `DDRangeConfig`, `DDConfiguration::toJSON`, `SystemDBWriteLockedNow`, `RangeConfigMapSnapshot`, and boost lexical integer parsing.

Control flow: The actor wraps usage/error handling in a local `fail` lambda, then consumes arguments from a list. `show [includeDefault]` reads a snapshot for all keys and prints JSON, optionally including default ranges. `update` and `set` require begin/end plus options, validate `end > begin`, construct a `DDRangeConfig`, parse option pairs (`replication <N>`, `teamID <N>`) or `default`, and call `updateRange` with a boolean indicating exact set vs incremental update. A generator supplies context-sensitive completion hints.

State and persistence behavior: Mutates persisted user range configuration through system DB write-locked DD configuration abstractions. The settings are hints consumed by DataDistribution and do not directly rewrite shard maps.

Dependencies and integration points: Integrates with fdbclient data-distribution configuration, system database write-lock wrappers, JSON rendering, and fdbcli help/completion.

Risks: The `updateRange` call is inside the option loop, so multiple options cause multiple writes as the config object accumulates. If that is intentional it still increases partial-progress considerations if a later option fails before subsequent writes. It does not validate range is within normal keys. Integer option validation is delegated to DD config layers.

Test signals: Cover show with/without defaults, update vs set semantics, default reset, multiple options, missing/invalid option arguments, inverted ranges, unknown commands/options, completion output, and DD config persistence.
