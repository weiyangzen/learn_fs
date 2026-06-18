# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOFS.java

Purpose: concrete OFS/rooted filesystem selector for legacy bucket layout without filesystem paths or extra feature flags.

Important APIs/types/functions: extends `AbstractRootedOzoneFileSystemTest` and calls `super(BucketLayout.LEGACY, false, false)`.

Control flow: local class only parameterizes the inherited rooted filesystem suite.

State and persistence behavior: inherited tests operate through `ofs://` volume/bucket-rooted paths with legacy layout semantics.

Dependencies and integration points: depends on `AbstractRootedOzoneFileSystemTest` and `BucketLayout.LEGACY`.

Risks: constructor flag order is compact and easy to misread; mistakes would route broad inherited coverage to a different layout or mode.

Test signals: inherited test failures point to OFS legacy-rooted behavior regressions.
