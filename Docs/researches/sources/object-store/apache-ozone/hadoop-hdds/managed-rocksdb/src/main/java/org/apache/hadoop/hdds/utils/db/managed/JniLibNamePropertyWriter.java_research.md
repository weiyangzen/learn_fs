<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/JniLibNamePropertyWriter.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/JniLibNamePropertyWriter.java

## Purpose

Small build-time utility that writes the platform-specific RocksDB JNI library name into a properties file for the native rocks-tools Maven profile.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `JniLibNamePropertyWriter`. Notable methods: `main`. Key imports include `java.io.IOException`, `java.io.OutputStreamWriter`, `java.io.Writer`, `java.nio.charset.StandardCharsets`, `java.nio.file.Files`, `java.nio.file.Paths`.

## Control flow

`main` takes the output path from `args[0]`, asks ManagedRocksObjectUtils for the RocksDB JNI file name, and writes `rocksdbLibName=...` as UTF-8.

## State and persistence behavior

Writes one build artifact file; no runtime persistence.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

No argument validation is present, and IO failures are printed rather than propagated, so Maven must detect missing/invalid property files.

## Test signals

Invoke with a temporary path and assert the property is written; test missing args and unwritable paths if build failure semantics matter.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/JniLibNamePropertyWriter.java -->
