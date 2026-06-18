# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ldb/ValueSchema.java

Purpose: `ValueSchema` prints a JSON description of the Java value type stored in a selected RocksDB column family.

Important APIs and types: It extends `AbstractSubcommand`, uses `DBDefinitionFactory`, `DBColumnFamilyDefinition`, `JsonUtils`, reflection `Field`, `ParameterizedType`, collection handling, and `OzoneConfiguration`.

Control flow: `call()` validates `--depth` in `[0,10]`, resolves the DB definition from parent `--db` and `--dn-schema`, resolves the column family, recursively walks non-static fields of the value class up to the requested depth, and prints a JSON map keyed by value type name.

State and persistence behavior: It reads no DB rows and writes no persistent state. It updates `DBDefinitionFactory`'s process-wide datanode schema version.

Dependencies and integration points: It complements `DBScanner` by showing users available field paths for projection/filtering.

Risks: Interface/abstract fields produce empty structures, collection generic types may not be simple classes, and reflection exposes private implementation fields that can change without serialized schema changes.

Test signals: Error for invalid depth, incorrect DB path, or missing table; JSON field tree for supported table values.
