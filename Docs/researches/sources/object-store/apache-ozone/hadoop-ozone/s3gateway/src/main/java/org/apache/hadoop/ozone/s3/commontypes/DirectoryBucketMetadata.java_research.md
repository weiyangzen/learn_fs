# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/DirectoryBucketMetadata.java

Purpose: `DirectoryBucketMetadata` represents one bucket row in the `ListDirectoryBuckets` response.

Important APIs and flow: JAXB fields include `Name`, `CreationDate`, `BucketRegion`, and `BucketArn`, with the date marshalled by `IsoDateAdapter`. It is a simple mutable bean populated by the directory-bucket listing endpoint.

State, dependencies, risks, and tests: state is transient response data. It integrates with `ListDirectoryBucketsResponse`. Risks include region/ARN semantics diverging from AWS directory bucket expectations and null field marshalling. Tests should assert XML shape and date formatting for directory bucket listings.
