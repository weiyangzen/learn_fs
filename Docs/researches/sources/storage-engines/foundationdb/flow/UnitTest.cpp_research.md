<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/UnitTest.cpp -->
# sources/storage-engines/foundationdb/flow/UnitTest.cpp
- Purpose: Registers Flow unit tests and stores simple test parameters.
- Important APIs/types/functions: Global `g_unittests`, `UnitTest::UnitTest`, and `UnitTestParameters` setters/getters for string, integer, double, and data directory.
- Control flow: Each static `UnitTest` prepends itself to the global linked list during static initialization. Parameter setters store stringified values in a map; typed getters parse with `atoll`/`atof` if present.
- State and persistence behavior: Test registry is process-global and in-memory. Parameters are per-run in-memory state. No persistence.
- Dependencies and integration points: Used by `TEST_CASE` macros and `UnitTestRunner.cpp`. Depends on Flow `Optional` and `format`.
- Risks: Static initialization order can matter across translation units. `atoll`/`atof` parsing is permissive and does not report invalid suffixes. `getDataDir()` assumes the optional data directory has been set.
- Test signals: Indirectly validated by every linked `TEST_CASE` and by `UnitTestRunner` collection/filtering.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/UnitTest.cpp -->
