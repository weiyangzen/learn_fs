## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/SchemaOneKeyCodec.java

Purpose: Encodes and decodes schema-one keys that historically mixed binary long block IDs and string metadata/prefixed keys in the same RocksDB column family.

Important APIs and functions: `toPersistedFormat()` encodes parseable numeric strings as `LongCodec`, otherwise as `StringCodec`. `fromPersistedFormat()` decodes bytes as string first, recognizes known metadata/prefixed block regexes, otherwise decodes 8-byte arrays as longs and all other arrays as strings. `copyObject()` returns the same immutable string.

Control flow and state: Singleton codec with trace logging for format decisions. Regexes distinguish keys like `#deleted#123` and short metadata keys from numeric block IDs.

Persistence and dependencies: Used by all schema-one logical column families. It depends on HDDS long/string codecs and is central to reading pre-codec schema-one DBs.

Risks: Ambiguous byte arrays can decode as a string if their string representation matches known regexes, even if originally a long. Numeric metadata-like strings without prefixes are stored as longs. Regex coverage must match every schema-one string key pattern.

Test signals: Round-trip numeric block IDs, metadata keys, deleted/deleting prefixes, non-8-byte strings, ambiguous 8-byte payloads, trace decision paths, and compatibility with existing schema-one RocksDB data.
