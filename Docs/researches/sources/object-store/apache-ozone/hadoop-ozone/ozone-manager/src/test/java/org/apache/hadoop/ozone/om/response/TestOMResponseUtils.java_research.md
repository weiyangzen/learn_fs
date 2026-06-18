# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/TestOMResponseUtils.java

Purpose: Shared test utility for OM response tests that need a representative `OmBucketInfo`.

Important APIs/types/functions: Defines a non-instantiable `TestOMResponseUtils` class with `createBucket(String volume, String bucket)`. The helper uses `OmBucketInfo.newBuilder`, `Time.now`, versioning, and a singleton metadata map.

Control flow: `createBucket` constructs an `OmBucketInfo` with volume and bucket names, current creation time, versioning enabled, and metadata `key1=value1`, then returns the built value.

State/persistence: No direct persistence. The returned object is later written by bucket, file, and FSO response tests into `bucketTable`.

Dependencies/integration: Used by bucket create/delete/property tests, directory create tests, FSO rename support, and other tests that need stable bucket metadata without repeating builder boilerplate.

Risks/test signals: Because creation time is dynamic, equality is reliable only against the exact returned object. The helper does not set object IDs unless callers rebuild it, so FSO tests that require IDs must add them explicitly.
