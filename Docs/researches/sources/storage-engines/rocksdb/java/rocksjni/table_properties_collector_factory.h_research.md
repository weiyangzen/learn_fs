<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table_properties_collector_factory.h -->
# sources/storage-engines/rocksdb/java/rocksjni/table_properties_collector_factory.h

Purpose: Declares the native wrapper used to pass a shared table properties collector factory through Java handles.

Important APIs/types/functions: `struct TablePropertiesCollectorFactoriesJniWrapper` contains `std::shared_ptr<rocksdb::TablePropertiesCollectorFactory> table_properties_collector_factories`.

Control flow: Allocation/deletion happens in `table_properties_collector_factory.cc`; other option bridges can reinterpret the handle and read the shared pointer field.

State and persistence behavior: Holds only process-local shared ownership of a collector factory.

Dependencies and integration points: Includes `rocksdb/table_properties.h` and `rocksdb/utilities/table_properties_collectors.h`. It is a C++ bridge type, not a generated JNI header.

Risks: The include guard name is generic (`ROCKSDB_TABLE_PROPERTIES_COLLECTOR_FACTORY_H`) and could collide with a broader RocksDB header guard. The plural field name is awkward and must be referenced exactly by consumers.

Test signals: Build tests should include this header with RocksDB headers in different orders. Runtime tests should verify option consumers correctly extract the shared pointer.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table_properties_collector_factory.h -->
