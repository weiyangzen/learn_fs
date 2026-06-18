# sources/object-store/minio/cmd/warm-backend-s3.go

Generic S3-compatible `WarmBackend`. It stores a `minio.Client`, `minio.Core`, bucket, prefix, and storage class. Put uploads with content MD5 and metadata; Get applies version/range options and uses core primitives; Remove supports versioned delete; InUse lists one prefix result.

Construction validates authentication combinations and bucket, then supports AWS IAM role, web identity role, or static credentials. The client uses endpoint host/scheme, global remote transport, configured region, and tier app info.

Remote state is S3 object data, metadata, and versions. Risks include auth ambiguity, prefix/listing semantics, host-only endpoint handling, range behavior for zero length, and error mapping coverage. No direct tests in this subset cover it.
