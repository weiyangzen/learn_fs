# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/DataDistributionConfig.h

Purpose: Declares user-controlled data distribution range configuration stored in system keyspace, including per-range replication factor and team-id overrides.

Important APIs/types/functions: `DDRangeConfig` stores optional `replicationFactor` and optional `teamID`, supports overlay `apply()`, equality, `toString()`, serialization, JSON conversion, and trace/fmt formatting. `DDConfiguration` is a `KeyBackedClass` under `\xff\x02/ddconfig/`, with `RangeConfigMap` over keys to `DDRangeConfig`, `userRangeConfig()` accessor, and static `toJSON()` for snapshots.

Control flow: Management or special-key code writes range-map entries. DD reads a local snapshot and applies optional overlays across ranges so unspecified fields inherit from preceding/default ranges. JSON conversion produces status/inspection output, optionally including default ranges.

State and persistence behavior: Configuration persists in key-backed range map entries. Because both fields are optional, absence means continuation/inheritance rather than an explicit default. Updating user range config fires the class trigger.

Dependencies and integration points: Depends on serialization, NativeAPI/SystemData/FDB types, key-backed types/range maps, RYW/run transaction helpers, `DatabaseContext`, and JSON. Integrated with data distribution team selection and management APIs.

Risks: Optional overlay semantics can be misread as explicit null/default, causing wrong replication or team isolation. `teamID` is advisory for keeping different IDs on different teams, not an enforcement guarantee. Prefix/key-backed layout changes would orphan existing config.

Test signals: Range map set/clear/read snapshots; overlay application across adjacent ranges; JSON output with and without default ranges; DD behavior with replication-factor and team-id overrides; trigger firing on updates.
