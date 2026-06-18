# sources/storage-engines/rocksdb/table/cuckoo/cuckoo_table_builder.h

Purpose: declares `CuckooTableBuilder`, the `TableBuilder` implementation for cuckoo-table SST files.

Important APIs/types/functions: public methods are constructor, `Add`, `status`, `io_status`, `Finish`, `Abandon`, `NumEntries`, `FileSize`, `GetTableProperties`, `GetFileChecksum`, and `GetFileChecksumFuncName`. Private structures and methods include `CuckooBucket`, `MakeSpaceForKey`, `MakeHashTable`, `IsDeletedKey`, `GetKey`, `GetUserKey`, and `GetValue`.

Control flow: the header contract requires keys to be added in comparator order and exactly one of `Finish`/`Abandon` before destruction. Builder state supports collecting entries first, then building the final hash table only at finish.

State and persistence: runtime state includes hash function count, file pointer, ratio/search/depth options, block size, current hash table size, last-level mode, fixed key/value lengths, concatenated key-value and deleted-key buffers, counts, status/io status, table properties, comparator, hash mode flags, smallest/largest user keys, and closure flag. This state is serialized into the file and property block during `Finish`.

Dependencies/integration: derives from `TableBuilder` and depends on version/table properties, writable file writer, comparator, and cuckoo table factory hash callback conventions.

Risks and test signals: the builder stores all keys and values in memory until finish, so memory grows with file size. It assumes fixed lengths and limited value types, making it unsuitable for snapshots/merge/prefix features. `cuckoo_table_builder_test.cc` exercises the public builder contract and many failure modes.
