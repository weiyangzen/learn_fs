# Research: sources/storage-engines/rocksdb/db_stress_tool/db_stress_filters.h

- **Purpose:** Declares the db_stress SST query filter configuration manager accessor.
- **Important APIs/types/functions:** Declares `experimental::SstQueryFilterConfigsManager& DbStressSqfcManager()` under `GFLAGS`.
- **Control flow:** Header only; implementation constructs and returns the manager in `.cc`.
- **State and persistence behavior:** No header state. The returned manager governs in-process SQFC configuration used by stress reads.
- **Dependencies and integration points:** Includes `rocksdb/experimental.h`; used by stress setup and range-query code that needs SQFC filters.
- **Risks:** API availability is gated on `GFLAGS`; callers must link `db_stress_filters.cc`.
- **Test signals:** Compile/link coverage and stress runs with `FLAGS_use_sqfc_for_range_queries`.
