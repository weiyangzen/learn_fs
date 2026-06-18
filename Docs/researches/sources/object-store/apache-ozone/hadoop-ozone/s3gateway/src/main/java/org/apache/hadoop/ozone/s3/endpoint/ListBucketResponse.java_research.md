# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListBucketResponse.java

Purpose: `ListBucketResponse` is the JAXB result model for root ListBuckets (`ListAllMyBucketsResult`).

Important APIs and flow: it wraps a `Buckets` list of `BucketMetadata` elements and an `Owner`. Root endpoint code appends bucket metadata and sets the owner before returning XML.

State, dependencies, risks, and tests: state is response-only. It integrates with root bucket listing and `BucketMetadata`. Risks are missing owner, incorrect wrapper element names, and bucket ordering/count mismatches. Tests should assert XML shape and `getBucketsNum` for list-buckets behavior.
