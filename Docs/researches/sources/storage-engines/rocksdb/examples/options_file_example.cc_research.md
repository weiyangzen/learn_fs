# sources/storage-engines/rocksdb/examples/options_file_example.cc

## Purpose
`options_file_example.cc` demonstrates using `rocksdb/utilities/options_util.h` to load persisted RocksDB options from a DB directory and reopen without manually reconstructing all scalar options.

## Important APIs and control flow
The example builds `DBOptions` with `create_if_missing`, two `ColumnFamilyDescriptor`s, a shared LRU cache, `BlockBasedTableOptions`, and a dummy compaction filter. It installs table factories and a non-owning compaction-filter pointer, destroys and opens the DB, creates `"new_cf"` so options are persisted, closes, then calls `LoadLatestOptions()` into `loaded_db_opt` and `loaded_cf_descs`.

After loading, it validates `create_if_missing`, obtains loaded `BlockBasedTableOptions` from the table factory, checks `block_size`, manually restores `block_cache`, confirms the compaction filter pointer is null after load, manually restores it, and reopens with the loaded descriptors. Handles are deleted before close.

## State, persistence, and integration
The DB path holds RocksDB's generated options file. Integration points include `ConfigOptions`, `LoadLatestOptions`, block-based table factories, cache ownership through `shared_ptr`, and pointer-valued option repair before `DB::Open()`.

## Risks and test signals
The loop over loaded column families always uses `loaded_cf_descs[0]` when fetching table options, likely a copy/paste issue that does not validate all CFs. Pointer-valued options are not serialized as live objects and must be restored manually; forgetting this can silently alter behavior. The example uses raw CF handles and fixed temp paths. Test signals are successful load, scalar option equality, table factory option preservation, explicit restoration of cache/filter pointers, and successful reopen with loaded options.
