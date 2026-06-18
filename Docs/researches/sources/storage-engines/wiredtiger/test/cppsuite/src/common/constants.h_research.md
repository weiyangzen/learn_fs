# sources/storage-engines/wiredtiger/test/cppsuite/src/common/constants.h

Purpose: Declares shared constants and preprocessor macros for cppsuite configuration and WiredTiger extension paths.

Important APIs/types/functions: declares component/config/timestamp constants, `DEFAULT_FRAMEWORK_SCHEMA`, statistics URI, tracking tables, and macros for Snappy compressor and reverse collator configuration/paths.

Control flow: header-only declarations and macros are consumed by many harness files during compilation.

State and persistence: macro values shape table creation configs and extension loading paths; tracking table constants define persistent metadata table names.

Dependencies/integration: imported by component, database, metrics, timestamp, and operation-tracking code; linked to definitions in `constants.cpp`.

Risks and test signals: `EXTSUBPATH` differs between CMake and autoconf layouts, so build definitions must match extension paths. Table/config key renames require synchronized defaults in test config metadata.
