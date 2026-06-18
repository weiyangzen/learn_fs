<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/version.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/version.h

Purpose: Exposes RocksDB compile-time version macros and runtime build-information helpers. Consumers use it for conditional compilation, artifact labeling, diagnostics, and command-line build banners.

Important APIs/types/functions: `ROCKSDB_MAJOR`, `ROCKSDB_MINOR`, `ROCKSDB_PATCH`, `ROCKSDB_MAKE_VERSION_INT`, `ROCKSDB_VERSION_INT`, and `ROCKSDB_VERSION_GE` provide macro-level version checks. `GetRocksBuildProperties`, `GetRocksVersionAsString`, and `GetRocksBuildInfoAsString` provide runtime strings and property maps.

Control flow: Macro expansion computes an integer version as major * 1,000,000 + minor * 1,000 + patch. Runtime functions are declarations whose implementations return immutable build properties and formatted version/build-info text.

State and persistence behavior: No persistent state is created. The property map returned by reference is process state owned by the implementation. Version macros affect build outputs and Java Makefile version extraction.

Dependencies and integration points: Depends on `rocksdb_namespace.h`, `string`, and `unordered_map`. Java Makefile reads this file to derive `ROCKSDB_MAJOR`, `ROCKSDB_MINOR`, and `ROCKSDB_PATCH`. Build info appears in tools, logs, and release artifacts.

Risks and edge cases: The note says main branch should carry the next planned release number, so downstream packagers must align these macros with released artifacts. Macro arithmetic assumes reasonably bounded major/minor/patch values and numeric literals.

Test signals: Build tests can verify `ROCKSDB_VERSION_GE` around boundary versions, and integration tests can check formatted version strings and build-info banners include the expected version.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/version.h -->
