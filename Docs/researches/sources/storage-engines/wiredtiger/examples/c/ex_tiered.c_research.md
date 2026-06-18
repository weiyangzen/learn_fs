# sources/storage-engines/wiredtiger/examples/c/ex_tiered.c

Purpose: demonstrates tiered storage using the local `dir_store` storage source.

Important APIs and control flow: helper `add_data` inserts integer keys; `show_data` scans and prints a table. `platform_supported` skips Windows. `main` builds an open config with `tiered_storage=(bucket,bucket_prefix,local_retention,name=dir_store)` and loads `libwiredtiger_dir_store.so`, creates home and bucket directories, opens the connection, creates one local-only table with `tiered_storage=(name=none)` and one default tiered table, inserts batches, performs a normal checkpoint, inserts more, performs `checkpoint("flush_tier=(enabled)")`, scans both tables, inserts more, performs another normal checkpoint, and scans again.

State and persistence: creates local WT_HOME files and a bucket subdirectory containing tiered objects after flush. The tiered table may span local and object storage after later writes.

Dependencies and integration: requires non-Windows platform support, built `dir_store` extension at a relative build path, filesystem directories, and WiredTiger tiered storage configuration.

Risks: hard-coded `BUILD_DIR "../../../"` assumes a build/run layout. It does not verify object contents directly. Local retention and flush behavior can change with tiered-storage implementation details.

Test signals: scans of local and tiered tables should show all inserted keys independent of whether data resides locally or in the bucket after `flush_tier`.
