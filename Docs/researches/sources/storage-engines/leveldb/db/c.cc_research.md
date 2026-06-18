<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/c.cc -->
# sources/storage-engines/leveldb/db/c.cc

## Purpose
C API implementation wrapping LevelDB C++ DB, options, iterators, write batches, snapshots, comparators, filter policies, cache, environment, and version helpers.

## Important APIs, Types, And Functions
Defines opaque structs from `leveldb/c.h`; exported functions include `leveldb_open/close`, `put/delete/write/get`, iterator navigation/access/error, snapshots, property/size/compact/destroy/repair, write batch operations, option setters, comparator/filter policy creation, Bloom filter wrapper, read/write option setters, LRU cache, default env, test directory, `leveldb_free`, and version functions.

## Control Flow
Most calls translate C pointer+length inputs into `Slice`, call the C++ API, and convert `Status` to `char** errptr` via `SaveError()`. Returned strings are heap-allocated copies for caller ownership. Custom comparator/filter structs subclass C++ virtual interfaces and dispatch to C callbacks.

## State And Persistence Behavior
Owns heap wrappers around C++ objects; DB operations mutate persistent LevelDB state; snapshots pin versions until release; write batches accumulate mutations in memory; cache/env wrappers control ownership flags.

## Dependencies And Integration Points
Depends on public LevelDB headers and C runtime allocation/string functions. Bridges to C++ APIs `DB`, `Options`, `ReadOptions`, `WriteOptions`, `WriteBatch`, `Iterator`, `Snapshot`, `Cache`, `Env`, `FilterPolicy`, and `Comparator`. Implements the stable C ABI consumed by non-C++ bindings and `db/c_test.c`; compiled into the main LevelDB library by CMake.

## Risks
Caller must free returned buffers with `leveldb_free`; iter key/value pointers are valid only while iterator state remains; custom callback lifetimes must outlive wrappers; `CopyString()` allocates exactly value length without null terminator by design for binary values.

## Test Signals
CMake builds `db/c_test.c`; broader coverage comes from language bindings and C API consumers exercising error propagation and object lifetimes.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/c.cc -->
