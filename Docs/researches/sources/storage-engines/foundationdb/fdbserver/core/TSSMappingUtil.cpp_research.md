# sources/storage-engines/foundationdb/fdbserver/core/TSSMappingUtil.cpp

## sources/storage-engines/foundationdb/fdbserver/core/TSSMappingUtil.cpp

Purpose: reads the mapping from storage server IDs to testing storage server interfaces from system keyspace metadata.

Important APIs: `readTSSMappingRYW` for `ReadYourWritesTransaction` and `readTSSMapping` for regular `Transaction`.

Control flow and state: the RYW variant uses `KeyBackedMap<UID, UID>` at `tssMappingKeys.begin` to read all UID pairs, asserts the result is below `CLIENT_KNOBS->TOO_MANY`, fetches the mapped TSS server-list value, decodes it, and stores it in the output `std::map<UID, StorageServerInterface>` keyed by source storage server ID. The regular transaction variant reads the raw key range, unpacks source IDs from tuple-encoded keys and TSS IDs from tuple-encoded values, then decodes corresponding server-list values.

Dependencies and integration: depends on `SystemData`, `KeyBackedTypes`, tuple codecs, `serverListKeyFor`, and `decodeServerListValue`. It integrates with TSS recruitment, data distribution checks, and simulation/performance testing paths needing source-to-TSS interface mappings.

Risks and tests: both functions assume server-list values exist and call `v.get()`, so corrupted/incomplete mappings will throw/assert. Large mappings are bounded by `TOO_MANY`. Tests should cover empty mapping, multiple TSS mappings, missing server-list entries, and both transaction APIs producing identical maps.
