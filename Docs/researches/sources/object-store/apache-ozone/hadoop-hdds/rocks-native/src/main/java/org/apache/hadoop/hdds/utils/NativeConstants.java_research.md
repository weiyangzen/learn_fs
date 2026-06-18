<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/NativeConstants.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/NativeConstants.java

## Purpose

Central constants for the rocks-native library name and system property key used by native RocksDB tooling.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils`. Main type: `NativeConstants`. Notable methods: constructor/overrides only. Key imports include none.

## Control flow

No control flow; consumers import constants.

## State and persistence behavior

No mutable state.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Changing the constant breaks resource names, Maven native packaging, and NativeLibraryLoader lookup.

## Test signals

Compile-time usage and NativeLibraryLoader tests pin the values indirectly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/NativeConstants.java -->
