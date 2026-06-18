
## sources/storage-engines/wiredtiger/ext/storage_sources/dir_store/CMakeLists.txt

Purpose: builds the directory-backed storage source extension target `wiredtiger_dir_store` from `dir_store.c`.

Integration: the target is a loadable `MODULE`, includes WiredTiger source/generated/config headers, and applies C diagnostic flags. This CMake file is the build entry point for the storage-source implementation but does not include install or builtin-mode logic.

State and persistence: no runtime state here; persistence behavior belongs to `dir_store.c`, which is outside this work item. Risks are target/source drift and module-only availability. Test signals include building the module, loading it through WiredTiger's storage source extension path, and verifying the target sees generated config headers.
