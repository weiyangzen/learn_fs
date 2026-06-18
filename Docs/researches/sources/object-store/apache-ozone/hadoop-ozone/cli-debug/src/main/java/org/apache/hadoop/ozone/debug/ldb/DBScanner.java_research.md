# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ldb/DBScanner.java

Purpose: `DBScanner` implements `ozone debug ldb scan`, decoding and printing rows from Ozone RocksDB column families with filtering, projection, count, range, batching, and output-file support.

Important APIs and types: It extends `AbstractSubcommand`, uses parent `RDBParser`, `DBDefinitionFactory`, `DBColumnFamilyDefinition`, `ManagedRocksDB`, `ManagedRocksIterator`, `ManagedReadOptions`, `ManagedSlice`, Ozone codecs for string/long/container/pipeline keys, `DatanodeSchemaThreeDBDefinition`, Jackson `ObjectMapper/ObjectWriter`, `Filter`, Java reflection `Field`, and a threaded `LogWriter`.

Control flow: `call()` opens the selected RocksDB read-only and delegates to `printTable`. `printTable` validates limits, resolves the DB definition/table, handles `--show-count`, creates an iterator, and applies schema-v3 container bounds when `--container-id` is set. `processRecords` seeks to `--startkey`, converts and filters values, batches key/value bytes, submits parsing tasks, observes limits/end key, and waits for futures. `Task` decodes keys/values, optionally projects nested fields, serializes JSON, and sends sequenced chunks to `LogWriter`, which preserves iterator order despite concurrent parsing.

State and persistence behavior: It reads RocksDB only unless `--out` is used, in which case it writes JSON output files and may suffix files by `--max-records-per-file`. Runtime state includes global count, file suffix, a static `compact` option, and a static volatile exception flag.

Dependencies and integration points: It is the main consumer of Ozone DB definitions and codecs for OM, SCM, Recon, and datanode DBs. It integrates schema-v3 container key prefix logic with debug output formatting.

Risks: Reflection-based filters/projections can break on private field renames and set fields accessible. The static `compact` and `exception` flags are process-wide. Output JSON formatting relies on comma insertion across batches; error paths can still print closing delimiters. File output assumes parentFile is non-null, so a bare filename may risk null handling.

Test signals: Decoded JSON for table rows, count output, start/end key behavior for supported key types, schema-v3 key rendering, field filtering/projection, valid output ordering under multiple threads, and non-zero exit behavior when DB/table/filter errors occur.
