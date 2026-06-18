# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableFormatConfig.java

## Purpose
`TableFormatConfig` is the abstract base for configuring a RocksDB table factory from Java.

## Important APIs and Types
It declares protected abstract `newTableFactoryHandle()`, which concrete table-format configurations implement to allocate a native table-factory handle.

## Control Flow
The method is intended to be called by `Options.setTableFormatConfig()`, which creates a native shared pointer to the corresponding C++ table factory.

## State and Persistence Behavior
The base class owns no state. Concrete subclasses hold configuration that affects future SST/table file format and layout.

## Dependencies and Integration Points
It integrates with `Options.setTableFormatConfig()` and concrete formats such as block-based or plain-table configs elsewhere in RocksJava.

## Risks and Test Signals
Tests should verify concrete subclass handles, options ownership/lifetime, and table files generated with each config. Because the method is protected and native ownership is external, lifecycle tests are important.
