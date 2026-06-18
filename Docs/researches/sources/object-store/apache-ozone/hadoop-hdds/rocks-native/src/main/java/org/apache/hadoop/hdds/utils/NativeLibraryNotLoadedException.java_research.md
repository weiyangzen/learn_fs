<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/NativeLibraryNotLoadedException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/NativeLibraryNotLoadedException.java

## Purpose

Checked exception indicating that a named native library could not be loaded.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils`. Main type: `NativeLibraryNotLoadedException`. Notable methods: constructor/overrides only. Key imports include none.

## Control flow

Constructor formats a message from the library name.

## State and persistence behavior

Inherited exception message only.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Callers must not swallow this when native functionality is required; tryLoadLibrary intentionally converts it to false.

## Test signals

Assert message content and propagation from ManagedRawSSTFileReader.loadLibrary.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/NativeLibraryNotLoadedException.java -->
