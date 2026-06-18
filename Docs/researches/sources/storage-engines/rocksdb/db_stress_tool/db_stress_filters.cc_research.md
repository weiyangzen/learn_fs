# Research: sources/storage-engines/rocksdb/db_stress_tool/db_stress_filters.cc

- **Purpose:** Builds db_stress SST query filter configuration fixtures for range-query filter testing.
- **Important APIs/types/functions:** Defines anonymous `VariableWidthExtractor` and `FixedWidthExtractor`, shared min/max filters for key segments 0-3, configuration sets `fooConfigs1`, `fooConfigs2`, `barConfigs2`, static manager data, and `DbStressSqfcManager()`.
- **Control flow:** Extractors split keys into segment endpoints either by variable zero-byte delimiters or fixed 8-byte chunks. `DbStressSqfcManager` constructs a shared `SstQueryFilterConfigsManager` once with two versions of named configs and returns it.
- **State and persistence behavior:** Maintains a process-static shared manager after first call. Filter configs affect SST/table query filtering metadata and range-query read behavior, not external files directly.
- **Dependencies and integration points:** Uses `rocksdb/experimental.h` SQFC APIs through `db_stress_filters.h`; consumed when stress flags enable SQFC for range queries.
- **Risks:** The `std::once_flag` is local non-static in the function while `mgr` is static; this means `call_once` does not actually provide persistent once semantics and initialization is attempted each call. Assertions catch manager creation failure only in debug builds.
- **Test signals:** Range queries using SQFC table filters, manager creation status, and correctness of prefix/range scan results under configured filter versions.
