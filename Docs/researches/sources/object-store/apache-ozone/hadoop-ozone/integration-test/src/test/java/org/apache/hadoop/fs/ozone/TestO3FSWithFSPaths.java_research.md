# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestO3FSWithFSPaths.java

Purpose: concrete O3FS selector for legacy buckets with filesystem-path handling enabled.

Important APIs/types/functions: extends `AbstractOzoneFileSystemTest` and calls `super(true, BucketLayout.LEGACY)`.

Control flow: no local test logic; inherited tests run with the filesystem-path flag enabled.

State and persistence behavior: parent tests exercise legacy-bucket directory semantics while OM filesystem-path support is active.

Dependencies and integration points: depends on the shared O3FS abstract test class and legacy bucket layout.

Risks: a one-argument flag flip changes expected path normalization and directory materialization behavior.

Test signals: inherited failures isolate regressions specific to O3FS legacy buckets when FS path mode is enabled.
