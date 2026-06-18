# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListMultipartUploadsResult.java

Purpose: `ListMultipartUploadsResult` is the JAXB XML response for listing active multipart uploads in a bucket.

Important APIs and flow: top-level fields capture bucket, key/upload markers, next markers, prefix, max uploads, truncation flag, and a list of `Upload` entries. Each upload includes key, upload ID, owner, initiator, storage class, and initiation time marshalled through `IsoDateAdapter`.

State, dependencies, risks, and tests: state is transient response data. It integrates with `ListMultipartUploadsHandler`, `S3Owner`, and `S3StorageType`. Risks include default owner/initiator values hiding real identity, null markers, and storage-class string compatibility. Tests should assert truncated and non-truncated XML, upload rows, and date formatting.
