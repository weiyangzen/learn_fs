<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/Makefile -->
# Research: sources/storage-engines/rocksdb/java/Makefile

Purpose: Provides the Make-based Java build, JNI header generation, dependency resolution, samples, tests, benchmarks, and static JNI packaging support for RocksDB's Java API.

Important APIs/types/functions: Major variables include `NATIVE_JAVA_CLASSES`, `NATIVE_JAVA_TEST_CLASSES`, `ROCKSDB_MAJOR/MINOR/PATCH`, `JAVA_TESTS`, source/class output directories, dependency jar paths and SHA256 values, Java command variables, plugin roots, and `ALL_JAVA_TESTS`. Targets include `java-version`, `clean`, `javadocs`, `javalib`, `java`, samples, dependency jar targets, `resolve_test_deps`, `java_test`, `test`, `run_test`, `run_plugin_test`, `db_bench`, and `pmd`.

Control flow: The Makefile discovers Java version/commands, includes plugin `.mk` files, expands core and plugin sources, downloads or copies test dependencies with checksum validation, compiles main classes with `javac -h` to generate JNI headers, compiles tests, runs JUnit via `RocksJunitRunner`, and compiles benchmark classes.

State and persistence behavior: Build products live in `target`, `benchmark/target`, `samples/target`, `include`, and `test-libs`. Dependency downloads are cached and checksum-verified. Sample targets create and remove temporary `/tmp/rocksdbjni` directories.

Dependencies and integration points: Depends on Java 8+, `javac`, `javadoc`, Maven for PMD, curl, SHA256 tool, local Maven repository fallback, plugin-provided Java sources/tests, and top-level RocksDB native build outputs. Version values are parsed from `../include/rocksdb/version.h`.

Risks and edge cases: Manual native class and test lists can lag new Java classes. Dependency downloads use `--insecure`, so checksum validation is essential. Java version parsing depends on `javac -version` token shape. Sample targets remove hard-coded temp paths.

Test signals: `make -C java java`, `java_test`, `test`, `db_bench`, `pmd`, dependency checksum failures, and JUnit output from `RocksJunitRunner` are the main health signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/Makefile -->
