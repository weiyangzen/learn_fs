# sources/storage-engines/foundationdb/fdbcli/LocationMetadataCommand.cpp

Purpose: Implements `location_metadata`, a diagnostic command for inspecting shard metadata, physical shard counts, range resolution, per-server shard assignments, and random shard samples.

Important APIs/types/functions: `locationMetadataCommandActor`, private helpers `describeServers`, `printKeyServersEntry`, `printRandomShards`, `printPhysicalShardCount`, `printServerShards`, and `resolveRange`. It uses `ReadYourWritesTransaction`, `serverListKeyFor`, `decodeServerListValue`, `decodeKeyServersValue`, `decodeServerKeysValue`, `serverTagKeys`, `keyServersPrefix`, `serverKeysPrefixFor`, `krmGetRanges`, `anonymousShardId`, and `DataMoveType`.

Control flow: `physicalshards` scans all key-server ranges and counts ranges whose decoded source shard id is not anonymous. `resolve` prints keyServers entries for a single key or range, including source/destination server descriptions resolved from server list entries. `servershards` scans a server's serverKeys prefix and prints assigned ranges and shard ids. `listshards <n> [physical]` scans keyServers ranges from `allKeys.begin`, printing the first `n` physical or non-physical shards encountered.

State and persistence behavior: Read-only against system key metadata. No local state or mutations.

Dependencies and integration points: Depends on the new location metadata encoding, server tag maps, server list decoding, key-range-map helpers, and lock-aware system reads. It complements audit commands that validate location metadata.

Risks: Several helper paths assume system metadata values are present and decodable, including `describeServers` calling `v.get()`. `std::stoi` and `UID::fromString` exceptions are not caught locally. Long scans over all keys can be expensive on large clusters.

Test signals: Cover each subcommand, physical vs non-physical filtering, server ID parsing, single key vs range resolution, empty or malformed server list entries, paging over keyServers/serverKeys, and invalid argument handling.
