# sources/storage-engines/rocksdb/src.mk

Purpose: Makefile source manifest defining RocksDB library, tool, test, benchmark, JNI, optional FAISS, range-tree, folly, and C/assembly source groups.

Important APIs/types/functions: variables include `LIB_SOURCES`, `LIB_SOURCES_ASM`, `LIB_SOURCES_C`, `WITH_FAISS_LIB_SOURCES`, `RANGE_TREE_SOURCES`, `TOOL_LIB_SOURCES`, `ANALYZER_LIB_SOURCES`, `MOCK_LIB_SOURCES`, `BENCH_LIB_SOURCES`, `STRESS_LIB_SOURCES`, `TEST_LIB_SOURCES`, `TOOLS_MAIN_SOURCES`, `BENCH_MAIN_SOURCES`, `TEST_MAIN_SOURCES`, `MICROBENCH_SOURCES`, and `JNI_NATIVE_SOURCES`.

Control flow: the make system includes these variables to assemble compilation units. A compiler probe conditionally enables PowerPC crc32c assembly/C sources. This subset's Windows/port/table files appear in `LIB_SOURCES`, so they are part of the RocksDB core library build.

State and persistence behavior: build metadata only; no runtime state. It determines which object files and tests are produced.

Dependencies and integration points: integrates with Makefile build targets and mirrors CMake/Buck-style source inventories. The listed tests include broad env, file, logger, table, compression, and utility coverage.

Risks and test signals: omissions or stale entries cause missing symbols or untested code. Whitespace/backslash errors can break make parsing. Full build, selected target build, and source-list consistency checks are useful.
