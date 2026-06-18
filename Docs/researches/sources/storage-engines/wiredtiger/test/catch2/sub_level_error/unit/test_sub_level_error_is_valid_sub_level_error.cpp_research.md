# Research: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_is_valid_sub_level_error.cpp

## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_is_valid_sub_level_error.cpp

Purpose: Unit test for `__wt_is_valid_sub_level_error`.

Important APIs/types: tests normal WiredTiger primary error codes and integer boundaries of the sub-level error range. The comment states valid sub-level codes range from `-32000` through `-32199` inclusive, with `WT_NONE` also valid.

Control flow: the test asserts normal codes such as `WT_ROLLBACK`, `WT_DUPLICATE_KEY`, `WT_ERROR`, `WT_NOTFOUND`, `WT_PANIC`, `WT_RESTART`, `WT_RUN_RECOVERY`, `WT_CACHE_FULL`, `WT_PREPARE_CONFLICT`, and `WT_TRY_SALVAGE` are not classified as sub-level errors. It then checks `WT_NONE`, lower/upper valid boundaries, and just-outside values.

State and persistence: no state or persistence; pure predicate testing.

Dependencies/integration: depends on the numeric allocation of primary and sub-level error namespaces. Risks are stale boundary assumptions if the reserved range changes. Test signals are boolean checks from `__wt_is_valid_sub_level_error`.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_is_valid_sub_level_error.cpp -->
