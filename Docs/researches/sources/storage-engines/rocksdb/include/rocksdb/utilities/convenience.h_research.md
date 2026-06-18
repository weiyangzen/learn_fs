# Research: sources/storage-engines/rocksdb/include/rocksdb/utilities/convenience.h

- **Purpose:** Compatibility forwarding header for code that still includes `rocksdb/utilities/convenience.h` after the real header moved to `rocksdb/convenience.h`.
- **Important APIs/types/functions:** No local APIs are declared; it includes `rocksdb/convenience.h`.
- **Control flow:** Preprocessor inclusion redirects callers to the new header location.
- **State and persistence:** No runtime state or persisted data.
- **Dependencies:** Depends on `rocksdb/convenience.h`.
- **Integration points:** Preserves source compatibility for existing applications and utilities using the old include path.
- **Risks:** Any symbols, dependencies, or warnings come from the forwarded header. Removing this shim would break old includes.
- **Test signals:** Compile tests should include both old and new header paths and verify the expected convenience APIs remain available.
