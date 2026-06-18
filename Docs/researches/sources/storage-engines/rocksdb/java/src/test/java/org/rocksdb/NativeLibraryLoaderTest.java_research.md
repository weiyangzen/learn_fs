## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/NativeLibraryLoaderTest.java

### Purpose

`NativeLibraryLoaderTest` verifies extraction of the RocksDB JNI library from the jar into a caller-specified temporary directory.

### Important APIs, Types, And Functions

It uses `NativeLibraryLoader.getInstance().loadLibraryFromJarToTemp`, `Environment.getJniLibraryFileName`, `TemporaryFolder`, `Files.exists`, and `Files.isReadable`.

### Control Flow

One test extracts the library and checks the expected platform-specific file exists and is readable. The second extracts twice into the same directory and asserts the originally returned file still exists, covering overwrite/replacement behavior.

### State And Persistence Behavior

The only persistent state is a native library file copied into JUnit temporary storage. No DB is opened.

### Dependencies And Integration Points

This integrates jar resource extraction, platform-specific JNI naming, filesystem permissions, and singleton loader behavior.

### Risks And Edge Cases

- Existing library replacement must handle platforms that lock loaded shared libraries.
- The expected filename depends on OS/architecture mapping in `Environment`.
- Tests validate readability but not that the extracted library can actually be loaded.

### Test Signals

Signals are file existence/readability and successful repeated extraction. Static research only; no test command was run.
