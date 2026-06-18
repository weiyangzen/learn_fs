# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOFSWithFSPaths.java

Purpose: concrete rooted OFS selector for legacy bucket layout with filesystem paths enabled.

Important APIs/types/functions: extends `AbstractRootedOzoneFileSystemTest` and invokes `super(BucketLayout.LEGACY, true, false)`.

Control flow: delegates entirely to inherited tests.

State and persistence behavior: inherited tests run on `ofs://` paths and verify legacy layout behavior under filesystem path support.

Dependencies and integration points: depends on rooted abstract test fixture and legacy layout.

Risks: relies on constructor flags for all behavior and contains no local assertions.

Test signals: inherited failures identify rooted OFS regressions in filesystem-path-enabled legacy buckets.
