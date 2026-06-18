# sources/storage-engines/rocksdb/table/table_properties.cc

Purpose: implements formatting, aggregation, serialization/parsing, equality, memory accounting, and compression display helpers for `TableProperties`.

Important APIs/types/functions: `TableProperties::ToString`, `Add`, `GetAggregatablePropertiesAsMap`, `ApproximateMemoryUsage`, `Serialize`, `Parse`, `AreEqual`, debug-only `TEST_SetRandomTableProperties`, and `ParseCompressionNameForDisplay`. The file defines all `TablePropertiesNames` persisted property-key strings and an `OptionTypeInfo` map describing how each field serializes.

Control flow: `ToString` appends human-readable property lines, including derived averages, unique ID, and sequence-number-to-time mapping. `Add` aggregates numeric counters across properties. Serialization delegates to `OptionTypeInfo` with the static field map. Compression display parsing handles old names directly and new format-version-7 compatibility-name plus hex-code lists with custom compression manager lookup.

State and persistence behavior: this file defines the canonical persisted property names for SST table properties and the parse/serialize shape for in-memory `TableProperties`. It does not own table files but controls metadata representation and diagnostics.

Dependencies/integration points: integrates with `SeqnoToTimeMapping`, `CompressionManager`, unique ID helpers, options type metadata, malloc usable-size support, random test helpers, and string utilities. Many table builders/readers rely on these property keys.

Risks: comments warn manual updates are required when new string properties are added to memory accounting and when the struct layout changes for debug randomization. Serialization correctness depends on `offsetof` entries matching `TableProperties`. Compression display intentionally differs from decompression validation by filtering invalid/no-compression codes for display.

Test signals: debug helper supports property serialization tests. Reader/dumper tests use properties for count verification, comparator selection, timestamp persistence, and external-SST metadata checks.
