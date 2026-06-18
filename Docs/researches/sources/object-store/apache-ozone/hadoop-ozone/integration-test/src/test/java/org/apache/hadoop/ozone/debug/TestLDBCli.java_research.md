# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/debug/TestLDBCli.java

Purpose: Integration tests for the `ozone debug ldb` CLI parser and scanner against temporary RocksDB stores. It validates table scanning, range and filter options, schema-aware datanode block table keys, output splitting, empty table output, and value-schema inspection.

Important APIs, types, and functions: Uses `RDBParser` through picocli `CommandLine`, `DBStoreBuilder`, `DBStore`, `Table`, `BlockUtils.getUncachedDatanodeStore`, `DatanodeSchemaThreeDBDefinition`, `DBScanner.JsonSerializationHelper`, `OmKeyInfo`, and `BlockData`. `scanTestCases` is the main parameter matrix. Helpers `prepareTable`, `prepareKeyTable`, `assertContents`, and `toMap` create expected JSON-compatible maps from production codecs.

Control flow: `setup` creates a fresh `OzoneConfiguration`, command-line parser, captured stdout/stderr writers, and an ordered expected map. Parameterized scan tests create either OM `keyTable`, DN `block_data` in schema V2/V3, or invalid combinations, execute `scan --db ... --column-family ...` with extra flags, then compare exit code, stderr substring, and parsed JSON output against an expected sub-map. Dedicated tests cover scanning an empty `pipelines` table, writing records into multiple output files using `--max-records-per-file` and `-l`, and running `value-schema`.

State and persistence behavior: Each test builds a temporary RocksDB directory and closes it after execution. OM key table state is populated with serialized `OmKeyInfo` values. DN block table state is populated with serialized `BlockData` values and schema-specific keys: plain block IDs for V2 and container-prefixed fixed-length keys for V3. Output-file tests persist JSON shard files under temp scan directories.

Dependencies and integration points: The tests connect the CLI parser, RocksDB abstraction, Ozone protobuf serialization, JSON object mapping, DN schema definitions, and filter/range logic. They use stdout/stderr exactly as the CLI would expose them.

Risks: JSON comparison depends on `DBScanner.JsonSerializationHelper` output structure. Filter strings are parsed as text and can be sensitive to field names such as `keyName` and `dataSize`. The test intentionally checks invalid V2-as-V3 parsing, so schema defaults are important. Output directory file counts assume deterministic splitting.

Test signals: Exit codes and stderr substrings validate error paths; JSON parsed stdout maps validate scan content; empty table output must be `{  }\n`; output files must be valid JSON; `value-schema` output must mention `keyName`.
