# Research: sources/storage-engines/rocksdb/db_stress_tool/db_stress_compression_manager.cc

- **Purpose:** Registers the db_stress custom compression manager with RocksDB's object registry.
- **Important APIs/types/functions:** Implements `DbStressCustomCompressionManager::Register`.
- **Control flow:** Uses `std::call_once` to allow unsupported format versions for tests and add a `CompressionManager` factory under the custom compatibility name.
- **State and persistence behavior:** Mutates the process-global object registry once. This enables later DB opens to read SSTs written with the custom compatibility name.
- **Dependencies and integration points:** Includes `db_stress_compression_manager.h` and `rocksdb/utilities/object_registry.h`; used by stress setup when custom compression manager mode is enabled.
- **Risks:** Registration must happen before reading files that require the custom compatibility name. `TEST_AllowUnsupportedFormatVersion()` affects test process behavior globally.
- **Test signals:** Successful DB reopen/read of SST files requiring `DbStressCustom1`; object-registry factory lookup.
