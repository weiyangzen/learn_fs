# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/BucketCrudHandler.java

Purpose: `BucketCrudHandler` handles plain bucket create and delete requests when no bucket subresource query parameter is present.

Important APIs and flow: `shouldHandle` excludes `?acl`, `?uploads`, and `?delete`. PUT sets the action to `CREATE_BUCKET`, calls `ObjectStore.createS3Bucket`, updates metrics, and returns HTTP 200 with `Location: /bucket`. DELETE optionally verifies expected bucket owner, calls `OzoneVolume.deleteBucket`, updates metrics, and returns 204.

State, dependencies, risks, and tests: no persistent state exists. It integrates with the bucket handler chain, Ozone object store/volume APIs, metrics, and owner verification. Risks include subresource detection gaps for future query parameters, create returning 200 instead of some AWS variants, and failure metrics not auditing directly except through the wrapper. Tests should cover normal create/delete, expected-owner condition, non-empty/missing bucket errors via OM mapping, and ignored subresource paths.
