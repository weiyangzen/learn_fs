# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/JNIUtil.java

## Purpose
`JNIUtil` loads FoundationDB native libraries either from explicit system properties, embedded classpath resources, or platform library search paths. It also exports embedded libraries to temporary files.

## Important APIs, Types, And Functions
`loadLibrary(String)` is the package-level loader used by `FDB` static initialization. `exportLibrary(String)` exposes resource extraction. Private helpers detect OS/arch, map library names, build resource paths, copy streams, and save resources as temp files.

## Control Flow
`loadLibrary` first checks `FDB_LIBRARY_PATH_<LIBNAME>` system property and calls `System.load` if present. Otherwise it detects the OS, maps the library name, verifies extension sanity, exports `/lib/<os>/<arch>/<mapped-name>` to a temp file, loads it, and eagerly deletes on Linux/macOS when possible. Missing embedded resources become `UnsatisfiedLinkError`.

## State And Persistence Behavior
The utility writes temporary files for embedded native libraries and marks them `deleteOnExit`. No long-lived Java state is stored.

## Dependencies And Integration Points
It depends on `System` properties, classpath resources, Java IO, and is called by `FDB` to load `fdb_c` and `fdb_java`.

## Risks And Edge Cases
Unsupported architectures or OS names throw immediately. Security managers can block property reads. Embedded resource absence, temp-file IO failures, or extension mismatches break native loading. Eager deletion is disabled on Windows.

## Test Signals
Packaging tests should cover resource paths for supported OS/arch pairs, property override loading, export failure when resource missing, macOS `.dylib` to `.jnilib` mapping, and temp-file cleanup flags.
