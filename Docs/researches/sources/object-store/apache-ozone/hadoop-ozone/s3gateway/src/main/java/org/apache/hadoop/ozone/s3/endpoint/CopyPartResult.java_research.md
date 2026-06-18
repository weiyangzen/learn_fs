# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/CopyPartResult.java

Purpose: `CopyPartResult` is the JAXB response for successful multipart `UploadPartCopy`.

Important APIs and flow: it exposes `LastModified` and `ETag`; the convenience constructor sets the ETag and `Instant.now()`. Object MPU copy-part handling returns this model after creating the copied part.

State, dependencies, risks, and tests: state is transient response data. It depends on `IsoDateAdapter` and S3 XML namespace constants. Risks include using gateway wall-clock time rather than storage commit time when the convenience constructor is used, and ETag quote handling. Tests should check XML output and timestamp/ETag expectations for copy part.
