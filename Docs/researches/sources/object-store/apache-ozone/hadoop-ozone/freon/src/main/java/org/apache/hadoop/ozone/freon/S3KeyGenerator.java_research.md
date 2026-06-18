# sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/S3KeyGenerator.java

## Purpose
`S3KeyGenerator` is a Freon command for creating S3 objects through Ozone's S3 gateway. It supports single-part `putObject` and multipart upload benchmarking.

## Important APIs, Types, and Functions
The command extends `S3EntityGenerator`, implements `Callable<Void>`, and is registered as `s3kg`/`s3-key-generator`. Options define bucket name, object or part size, multipart mode, and part count. `call()` validates multipart minimum part size against `OM_MULTIPART_MIN_SIZE`, initializes the S3 client, generates a reusable ASCII content string, disables AWS SDK put-object MD5 validation, creates the `key-create` timer, and runs `createKey()`. Multipart uploads use `InitiateMultipartUploadRequest`, `UploadPartRequest`, `PartETag`, and `CompleteMultipartUploadRequest`.

## Control Flow
Each iteration times one object creation. In multipart mode, the command initiates an upload, uploads `numberOfParts` parts from byte-array streams over the same content, tracks returned ETags, and completes the upload. In single-part mode, it calls `putObject(bucketName, generateObjectName(counter), content)`.

## State and Persistence Behavior
Persistent output is S3 objects in the target bucket. The command holds a single generated content string reused across all iterations and parts. Multipart state is transient upload ID and part ETags.

## Dependencies and Integration Points
It uses the AWS S3 SDK, Ozone multipart minimum-size constant, inherited S3 endpoint/client setup, and Freon object naming from `BaseFreonGenerator.generateObjectName()`.

## Risks and Edge Cases
The content string is converted to UTF-8 bytes for multipart uploads while `fileSize` is also passed as part size. Because `RandomStringUtils.nextAscii(fileSize)` uses ASCII characters, UTF-8 byte length should match character count. Multipart uploads are not explicitly aborted on intermediate failure. Disabling SDK MD5 validation improves benchmark throughput but removes a client-side integrity check.

## Test Signals
No direct unit test is present. Useful validation requires live S3 gateway tests for both single-part and multipart paths.
