<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/util/FileUtils.java -->
# Research: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/util/FileUtils.java

Purpose: Provides a small recursive delete utility for JMH benchmarks so temporary RocksDB directories are removed after each trial.

Important APIs/types/functions: `FileUtils.delete(Path)` and private `DeleteDirVisitor` extending `SimpleFileVisitor<Path>` are the core. Visitor methods override `visitFile` and `postVisitDirectory`.

Control flow: `delete` checks whether the path is a directory. Non-directories are deleted with `Files.deleteIfExists`; directories are traversed with `Files.walkFileTree`, deleting files as visited and deleting directories after their children.

State and persistence behavior: This utility destructively removes filesystem paths. Deletion of a directory is not atomic, and partial deletion can occur before an `IOException` is thrown.

Dependencies and integration points: Depends on Java NIO `Files`, `Path`, `SimpleFileVisitor`, and `BasicFileAttributes`. It is used by the JMH benchmark teardown methods.

Risks and edge cases: It follows normal `walkFileTree` behavior and does not include retry logic for open files, permissions, or Windows delayed deletion. If benchmark handles remain open, directory removal can fail.

Test signals: Successful benchmark teardown with no leftover temporary directories. Unit tests could create nested files/directories and verify full deletion plus error propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/util/FileUtils.java -->
