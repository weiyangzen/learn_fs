# sources/storage-engines/foundationdb/fdbrpc/ReplicationTypes.cpp

`ReplicationTypes.cpp` defines shared globals for replication locality types.

It provides `const std::vector<LocalityEntry> emptyEntryArray` and mutable process-global `int g_replicationdebug`. There is no active runtime control flow.

`emptyEntryArray` is immutable helper state used by replication policy selection when there are no preselected servers. `g_replicationdebug` controls verbose locality display/debug behavior in replication policy code. Neither value is persisted to disk.

The file depends on `fdbrpc/ReplicationTypes.h` and integrates with `ReplicationPolicy.cpp`. Risks are limited but real: mutable global debug state affects behavior process-wide, and `emptyEntryArray` should remain read-only. Coverage is indirect through replication policy serialization and selection tests.
