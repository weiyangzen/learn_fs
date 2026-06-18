# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/NativeLibraryLoader.java research

## Purpose

`NativeLibraryLoader` loads the RocksDB JNI library for Java clients. It first tries libraries available through `java.library.path`, then falls back to extracting a bundled JNI library resource from the jar into a temporary file and loading it.

## Important APIs and types

`getInstance()` returns the singleton. `loadLibrary(String tmpDir)` is synchronized and tries `System.loadLibrary(sharedLibraryName)`, `System.loadLibrary(jniLibraryName)`, optional fallback JNI library name, and finally `loadLibraryFromJar(tmpDir)`. `loadLibraryFromJarToTemp()` locates primary or fallback resource names. `createTemp()` creates either a JVM temp file or a named file under a caller-provided directory.

## Control flow

The load sequence catches `UnsatisfiedLinkError` from path-based attempts and optionally prints diagnostics when `ROCKS_JAVA_DEBUG_NLL=true`. Jar extraction uses `getClass().getClassLoader().getResourceAsStream`, copies with `Files.copy(..., REPLACE_EXISTING)`, marks temp files for deletion on exit, and calls `System.load()` once guarded by `initialized`.

## State and persistence behavior

Static state includes computed platform-specific library names and the `initialized` flag for jar loading. Extracted native libraries are temporary filesystem artifacts and registered for deletion on JVM exit; provided `tmpDir` files are overwritten after deletion.

## Dependencies and integration points

It depends on `org.rocksdb.util.Environment`, `java.io`, and NIO file copying. It is used by `RocksDB.loadLibrary()` and indirectly by constructors that need native methods.

## Risks and test signals

Risks include classloader resource absence, tmpDir not existing, stale files that cannot be deleted, concurrent load behavior across classloaders, and `initialized` only guarding the jar path. Tests should simulate path-load success, jar extraction success, fallback resource success, missing resources, invalid tmpDir, debug logging, and repeated synchronized calls.
