<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/CMakeLists.txt -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/CMakeLists.txt

## Purpose

Configures the CMake build for the `ozone_rocksdb_tools` shared JNI library used by Ozone's raw SST reader support.

## Important APIs, types, and functions

Important build commands include `find_package(JNI REQUIRED)`, `include_directories(${JNI_INCLUDE_DIRS})`, optional inclusion of RocksDB headers and `rocks_tools`, `add_library(ozone_rocksdb_tools SHARED ...)`, and `target_link_libraries` against RocksDB and rocks_tools.

## Control flow

CMake requires `GENERATED_JAVAH`, includes generated JNI headers, optionally configures SST dump sources when `SST_DUMP_INCLUDE` is set, imports the static `librocksdb_tools.a`, builds a shared library, and sets rpath/link flags.

## State and persistence behavior

Build state is contained in CMake/Maven target directories. The output shared library becomes a runtime resource loaded by NativeLibraryLoader.

## Dependencies and integration points

Depends on JNI headers, generated javah/javac headers, RocksDB headers and libraries, the RocksDB tools static library, and Maven properties passed by the rocks-native profile.

## Risks and edge cases

The `_GLIBCXX_USE_CXX11_ABI=0` flag, C++ standard, RocksDB version, and linked static library must match rocksdbjni. Missing `GENERATED_JAVAH` fails the configure step by design.

## Test signals

Run the rocks_tools_native Maven profile on a Linux builder, inspect the packaged shared object, and execute ManagedRawSSTFileReader integration tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/CMakeLists.txt -->
