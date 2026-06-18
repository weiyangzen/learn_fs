# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFSBucketLayout.java

Purpose: parameterized abstract test for OFS default bucket-layout configuration and validation when filesystem operations create buckets.

Important APIs/types/functions: `validDefaultBucketLayouts` returns empty/default, FSO, and LEGACY. `invalidDefaultBucketLayouts` returns an unknown value and OBJECT_STORE. `fileSystemWithUnsupportedDefaultBucketLayout` expects OMException messages; `fileSystemWithValidBucketLayout` creates a bucket through `fs.mkdirs` and checks actual `OzoneBucket.getBucketLayout`. `configWithDefaultBucketLayout` writes `OzoneClientConfig.fsDefaultBucketLayout` into a fresh configuration.

Control flow: setup obtains a cluster client, object store, OFS root URI, and a volume. Each parameter builds a new `OzoneConfiguration`, creates a new filesystem, and either expects construction failure or creates a bucket path `/volume/bucket-layout-suffix`.

State and persistence behavior: valid cases persist newly created buckets in OM with the requested layout. Invalid cases should fail before creating filesystem-visible state. Empty config maps to `OzoneClientConfig.Defaults.OZONE_CLIENT_FS_DEFAULT_BUCKET_LAYOUT`.

Dependencies and integration points: uses `NonHATests.TestCase`, `ObjectStore`, `OzoneBucket`, `OzoneClientConfig`, `FileSystem.newInstance`, and OFS URI scheme.

Risks: error-message assertions are specific. Bucket names are deterministic by layout, so repeated runs in one shared cluster depend on isolated test state or unique volume setup.

Test signals: detects unsupported default layout acceptance, OBJECT_STORE misuse for filesystem semantics, and drift between client config and actual bucket creation layout.
