# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestO3FS.java

Purpose: concrete O3FS test selector for the shared non-rooted filesystem suite using legacy bucket layout and non-filesystem-path behavior.

Important APIs/types/functions: package-private `TestO3FS` extends `AbstractOzoneFileSystemTest` and calls `super(false, BucketLayout.LEGACY)`. `@TestInstance(PER_CLASS)` lets inherited setup share class lifecycle.

Control flow: no local tests; JUnit runs inherited tests from the abstract superclass with constructor-supplied parameters.

State and persistence behavior: inherits all cluster, bucket, filesystem, listing, delete, and rename state behavior from the parent suite, specifically under O3FS URI authority semantics.

Dependencies and integration points: depends on `AbstractOzoneFileSystemTest` and `BucketLayout.LEGACY`.

Risks: small selector can silently change large inherited coverage if constructor flags are modified. It does not contain assertions itself.

Test signals: any failure comes from inherited O3FS legacy behavior tests.
