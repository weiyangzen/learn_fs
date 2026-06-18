<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/CMakeLists.txt -->
# Research: sources/storage-engines/rocksdb/java/CMakeLists.txt

Purpose: Defines the CMake-based Java/JNI build for RocksDB. It compiles Java classes, generates JNI headers, builds native `rocksdbjni` libraries, packages platform-specific JARs, generates javadocs/source jars, downloads Java test dependencies, and registers JUnit tests.

Important APIs/types/functions: Key variables include dependency versions, `JNI_NATIVE_SOURCES`, `JAVA_MAIN_CLASSES`, `JAVA_TEST_CLASSES`, `JAVA_TEST_RUNNING_CLASSES`, `JAVA_TESTCLASSPATH`, `JNI_OUTPUT_DIR`, `ROCKSDBJNI_STATIC_LIB`, `ROCKSDBJNI_SHARED_LIB`, `ROCKSDB_JAVADOC_JAR`, `ROCKSDB_SOURCES_JAR`, and `ROCKSDB_JAR`. Important CMake commands are `find_package(JNI)`, `add_jar`, `create_javah`, `add_library`, `target_link_libraries`, `create_javadoc`, `add_custom_target`, and `add_test`.

Control flow: The script validates Java/CMake compatibility, builds the main/test Java jars and native headers, downloads test jars when missing, handles old CMake/JDK header generation separately, builds native JNI shared libraries from the listed C++ sources, derives platform-specific names, packages native library plus `HISTORY-JAVA.md` into the Java jar, then registers each test class with `ctest`.

State and persistence behavior: Outputs are generated under the CMake build tree and `java/include`; test jars are cached under `java/test-libs`. The script mutates build artifacts only, but downloaded jars and generated headers affect subsequent incremental builds.

Dependencies and integration points: Depends on CMake Java support, JNI, RocksDB static/shared libraries, Java 8+, platform naming conventions, JUnit/Hamcrest/Mockito/CGLIB/AssertJ jars, and every Java/JNI file named in the large source lists. It complements the Java Makefile path.

Risks and edge cases: Source lists are manually maintained and can drift from the tree. Old CMake/JDK combinations need `javah`; Java 10+ requires CMake 3.11.4+. Test dependency downloads rely on an S3 mirror or `CUSTOM_DEPS_URL` without checksum checks in this file. Duplicate test class entries can cause redundant work.

Test signals: Successful `rocksdbjava`, `rocksdb_javadocs_jar`, and `rocksdb_sources_jar` targets; platform jar contents containing the correct native library; generated JNI headers; and passing `ctest` `jtest_*` entries with `-Xcheck:jni`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/CMakeLists.txt -->
