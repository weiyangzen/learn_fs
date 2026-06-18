<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/CMakeLists.txt -->
# sources/storage-engines/foundationdb/bindings/java/CMakeLists.txt

Purpose: CMake build graph for FoundationDB Java bindings, JNI library, Java workload library, jars, javadoc, fat jar packaging, and optional JUnit/integration tests.

Important build APIs/targets: cache toggles `RUN_JAVA_TESTS`, `RUN_JUNIT_TESTS`, `RUN_JAVA_INTEGRATION_TESTS`; source lists `JAVA_BINDING_SRCS` and `JAVA_TESTS_SRCS`; `vexillographer_compile` target `fdb_java_options`; generated `ApiVersion.java`; native targets `fdb_java` and `java_workloads`; `add_jar(fdb-java)`, `create_javadoc`, `CopyJavadoc`, `foundationdb-tests`, `fdb-java-tests`, `fat-jar`, optional `fdb-junit` and integration test targets.

Control flow: configure generated Java option/API files, choose OS/architecture packaging names, build JNI shared/object libraries, compile Java 8 sources, write OSGi-style manifest, create main jar, copy javadocs, unpack jar into a fat-jar staging dir, copy native libraries under platform-specific `lib/<os>/<arch>`, build release/snapshot fat jar and test jar, optionally download pinned JUnit jars and register ctest commands.

State and persistence: writes generated Java sources, manifest, javadocs, staged fat jar tree, native library copies, packages, and optional downloaded dependencies in build directories.

Dependencies and integration: requires Java/JNI CMake support, `fdb_c`, `fdb_java_native` generated headers, `flow`, `src/tests.cmake`, API version file, packaging target `packages`, and FoundationDB test macros.

Risks: network downloads during configure/build can fail; one `opentest4j` download lacks `EXPECTED_HASH`; sanitizer builds skip Java tests. Platform library destinations must stay aligned with runtime loader expectations. Linker version-script flags are Linux-specific with Clang 19 workaround.

Test signals: optional JUnit and integration ctest targets; integration tests require running FDB clusters and external client artifacts for multi-client paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/CMakeLists.txt -->
