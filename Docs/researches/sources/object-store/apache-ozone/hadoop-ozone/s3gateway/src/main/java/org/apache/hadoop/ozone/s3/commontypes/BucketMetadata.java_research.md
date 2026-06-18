# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/BucketMetadata.java

Purpose: `BucketMetadata` is the JAXB model for one bucket entry in `ListAllMyBucketsResult`.

Important APIs and flow: it has `Name` and `CreationDate` XML fields, with `Instant` marshalled through `IsoDateAdapter`. Getters and setters are simple bean accessors used by root listing responses.

State, dependencies, risks, and tests: state is transient response data only; no persistence exists. It integrates with `ListBucketResponse` and root endpoint bucket iteration. Risks are null dates/names and formatting compatibility with AWS clients. Tests should marshal list-buckets XML and assert name/date elements.
