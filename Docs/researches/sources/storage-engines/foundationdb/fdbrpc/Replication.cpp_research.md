# sources/storage-engines/foundationdb/fdbrpc/Replication.cpp

`Replication.cpp` is a minimal translation unit for the replication API declared in `fdbrpc/Replication.h`.

It only includes the header and implements no functions, control flow, state, or persistence. Implementation lives in headers or related files such as `ReplicationPolicy.cpp` and `ReplicationTypes.cpp`.

Its integration role is build-structure participation: the replication header has a compiled source unit in fdbrpc. The main risk is mistaking the file for unused dead weight when it may be required by build organization or future non-inline code. Test coverage is indirect through replication policy serialization and higher-level data-placement tests.
