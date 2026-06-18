<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/NativeLibraryLoader.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/NativeLibraryLoader.java

## Purpose

Loads Ozone native libraries from the system library path or from jar resources copied to a temporary directory, tracking loaded status per library name.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils`. Main type: `NativeLibraryLoader`. Notable methods: `initNewInstance`, `getInstance`, `getJniLibraryFileName`, `getJniLibraryFileName`, `isMac`, `isWindows`, `isLinux`, `appendLibOsSuffix`, `isLibraryLoaded`, `isLibraryLoaded`, `loadLibrary`, `copyResourceFromJarToTemp`. Key imports include `static org.apache.hadoop.hdds.utils.NativeConstants.ROCKS_TOOLS_NATIVE_LIBRARY_NAME`, `com.google.common.annotations.VisibleForTesting`, `java.io.File`, `java.io.IOException`, `java.io.InputStream`, `java.nio.file.Files`, `java.nio.file.Path`, `java.nio.file.StandardCopyOption`, `java.util.ArrayList`, `java.util.List`.

## Control flow

`loadLibrary` first tries System.loadLibrary. If that fails, it copies the OS-suffixed library and dependent files from classpath resources to a temp directory, calls System.load, schedules temp cleanup with ShutdownHookManager, records success/failure, and returns loaded state.

## State and persistence behavior

Maintains a singleton ConcurrentHashMap of library-name to loaded boolean and creates temporary native-library directories.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

A failed first load is cached as false but future calls still retry. Dependent resource streams are not null-checked before copy. OS detection is simple prefix matching, and temp cleanup depends on shutdown hooks.

## Test signals

The included tests mock resources and properties; also test unsupported OS suffixes, missing dependent files, repeated load calls, and custom native.lib.tmp.dir.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/NativeLibraryLoader.java -->
