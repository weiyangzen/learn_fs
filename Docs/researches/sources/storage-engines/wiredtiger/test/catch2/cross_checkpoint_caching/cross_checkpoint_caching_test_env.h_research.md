<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/cross_checkpoint_caching_test_env.h -->
# sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/cross_checkpoint_caching_test_env.h

Purpose: Declares the reusable cross-checkpoint cache test fixture.

Important APIs/types/functions: Constants `CROSS_CHECKPOINT_CACHING_TEST_HASH_SIZE` and `CROSS_CHECKPOINT_CACHING_TEST_DATA_SIZE`; class `cross_checkpoint_caching_test_env` with disabled copying, accessors, `put`, and `bucket_size`.

Control flow: Header declares fixture lifecycle managed by constructor/destructor in the `.cpp`.

State and persistence behavior: Holds `connection_wrapper`, `WT_SESSION_IMPL *`, `WT_CURSOR *`, and disaggregation sentinel.

Dependencies and integration points: Included by all cross-checkpoint cache unit tests; pulls in Catch2 and `connection_wrapper`.

Risks and test signals: Fixture owns real connection/cursor resources. Build and runtime cleanup tests are important to avoid DB_HOME contamination across Catch2 sections.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/cross_checkpoint_caching_test_env.h -->
