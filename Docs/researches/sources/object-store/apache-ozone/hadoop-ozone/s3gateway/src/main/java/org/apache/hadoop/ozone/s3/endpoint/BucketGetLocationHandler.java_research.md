# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/BucketGetLocationHandler.java

Purpose: `BucketGetLocationHandler` explicitly handles `GET Bucket ?location` by returning `NotImplemented` instead of falling through to list-objects.

Important APIs and flow: `handleGetRequest` checks the `location` query parameter. If absent, it returns null for the chain. If present, it sets `S3GAction.GET_BUCKET_LOCATION` and throws `NOT_IMPLEMENTED` for `GetBucketLocation`.

State, dependencies, risks, and tests: no state or persistence exists. It integrates with the bucket handler chain and audit wrapper. Risk is that AWS-compatible clients expecting location responses fail, but explicit not-implemented behavior is clearer than an incorrect XML body. Tests should verify `?location` claims the request and plain GET bucket still lists objects.
