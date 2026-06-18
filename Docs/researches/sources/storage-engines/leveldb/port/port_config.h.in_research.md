# sources/storage-engines/leveldb/port/port_config.h.in

Purpose: CMake configuration template for feature-detection macros used by LevelDB's port layer.

Important APIs and macros: `HAVE_FDATASYNC`, `HAVE_FULLFSYNC`, `HAVE_O_CLOEXEC`, `HAVE_CRC32C`, `HAVE_SNAPPY`, and intended `HAVE_ZSTD`.

Control flow: CMake replaces `#cmakedefine01` entries with 0/1 definitions unless the macro is already defined externally.

State and persistence behavior: compile-time only. Feature flags alter sync behavior, compression availability, and accelerated checksum paths.

Dependencies and integration: consumed by platform port implementations and build system generated headers.

Risks and edge cases: the guard uses `#if !defined(HAVE_Zstd)` but defines/checks `HAVE_ZSTD`, a spelling inconsistency that could surprise external defines. Incorrect feature detection can silently disable compression or fsync variants.

Test signals: build configuration and compression/sync tests validate generated output.
