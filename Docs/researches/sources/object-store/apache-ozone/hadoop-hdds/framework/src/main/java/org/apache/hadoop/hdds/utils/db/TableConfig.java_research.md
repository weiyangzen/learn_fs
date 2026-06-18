# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/TableConfig.java

## Purpose

`TableConfig` describes a RocksDB column family/table name and its managed column family options. The complete 123-line source was read for this report.

## Important APIs, Types, and Functions

Important methods are `toName(byte[])`, `newTableConfig(Path,String)`, `getName`, `getDescriptor`, `getColumnFamilyOptions`, `equals`, `hashCode`, `toString`, and `close`.

## Control Flow

`newTableConfig` attempts to read per-column-family options from DB config files, falls back to the HDDS default DB profile if unavailable, then creates a config. `getDescriptor` clones managed options into a new `ColumnFamilyDescriptor`. Equality is based only on table name.

## State and Persistence Behavior

The object owns a `ManagedColumnFamilyOptions` instance that must be closed unless it is marked reused. It does not persist data but can load RocksDB options from files and supply descriptors for persistent column families.

## Dependencies and Integration Points

It depends on `DBConfigFromFile`, `DBStoreBuilder.HDDS_DEFAULT_DB_PROFILE`, `ManagedColumnFamilyOptions`, `ColumnFamilyDescriptor`, and HDDS `StringUtils`. `RocksDatabase.open` consumes sets of `TableConfig`.

## Risks and Edge Cases

The catch in `newTableConfig` ignores `RocksDBException`, so option-file failures silently use defaults. Equality ignores options, so two configs with the same name but different options collapse in sets. Ownership of managed options must be clear to prevent native leaks or double close.

## Test Signals

Tests should verify descriptor names/options, fallback on missing option files, equality by name, and close behavior for reused versus non-reused options.
