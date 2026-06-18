# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/CopyObjectResponse.java

Purpose: `CopyObjectResponse` is the JAXB result for successful S3 CopyObject.

Important APIs and flow: it contains `LastModified` marshalled through `IsoDateAdapter` and `ETag`. Object copy handling fills the values from the created/copied Ozone key metadata.

State, dependencies, risks, and tests: state is response-only. It depends on JAXB, `IsoDateAdapter`, and Ozone ETag metadata. Risks include ETag quote compatibility and timestamp precision/timezone. Tests should assert copy-object response XML and metadata propagation.
