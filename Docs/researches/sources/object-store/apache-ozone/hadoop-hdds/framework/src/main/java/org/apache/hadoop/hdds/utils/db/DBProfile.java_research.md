# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBProfile.java

## Purpose
`DBProfile` provides predefined RocksDB tuning profiles for HDDS metadata stores: `SSD`, `DISK`, and `TEST`.

## Important APIs and Types
Each enum implements `getDBOptions`, `getColumnFamilyOptions`, and `getBlockBasedTableConfig`. `SSD` configures write buffer size, dynamic level bytes, block cache, block size, pinned filters/indexes, bloom filter, parallelism, background compactions/flushes, bytes-per-sync, and create-if-missing flags. `DISK` adds compaction readahead and level compaction. `TEST` disables auto compactions.

## Control Flow and State
Every call creates new managed RocksDB option/config objects. `DISK` and `TEST` start from `SSD` options and mutate profile-specific fields. `toLong` converts storage-size doubles via `BigDecimal`.

## Persistence, Dependencies, and Integration
No persistence occurs directly. Dependencies include Hadoop `StorageUnit`, managed RocksDB option wrappers, LRU cache, bloom filter, and RocksDB `CompactionStyle`. `DBStoreBuilder` selects a default profile from `HDDS_DB_PROFILE`.

## Risks and Test Signals
Managed options contain native resources and must be closed by the owning store/build path. Profiles encode operational defaults, so changes affect memory and compaction behavior broadly. Tests should cover independent object creation, key option values, TEST compaction disabling, DISK readahead, and resource cleanup by builder/store paths.
