# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MultipartKeyHandler.java

Purpose: `MultipartKeyHandler` handles object-key multipart operations that are not POST: list parts and abort multipart upload.

Important APIs and flow: GET claims requests with `uploadId`, sets `LIST_PARTS`, parses `max-parts` and `part-number-marker`, and calls `listParts`. DELETE claims non-empty `uploadId`, sets `ABORT_MULTIPART_UPLOAD`, and calls `ClientProtocol.abortMultipartUpload`. `listParts` calls `OzoneBucket.listParts`, fills `ListPartsResponse`, maps storage class and truncated next marker, converts part metadata to response parts, and maps missing upload/access errors to S3 errors.

State, dependencies, risks, and tests: no persistent state exists. It integrates with object handler chains, Ozone multipart APIs, metrics, `ListPartsResponse`, and S3 error table. Risks include no explicit max-parts lower/upper validation here, integer parsing exceptions, ETag fallback to part name, and access-denied mapping depending on OM result codes. Tests should cover list parts, abort, missing upload, access denied, part marker parsing, truncation, and metric updates.
