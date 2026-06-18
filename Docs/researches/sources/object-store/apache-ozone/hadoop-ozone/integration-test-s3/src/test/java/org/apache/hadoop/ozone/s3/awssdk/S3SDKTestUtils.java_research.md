# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/awssdk/S3SDKTestUtils.java

## Purpose

This utility class supports AWS SDK S3 compatibility tests with digest calculation, random test-file creation, multipart upload ID extraction, and low-level presigned URL HTTP calls.

## Important APIs, types, and functions

The public API includes `UPLOAD_ID_PATTERN`, `calculateDigest(InputStream, int, int)`, `createFile(File, int)`, `extractUploadId(String)`, and `openHttpURLConnection(URL, String, Map<String, List<String>>, byte[])`. It uses `MessageDigest` MD5, `InputSubstream`, `RandomUtils.secure()`, `RandomAccessFile`, Apache Commons IO, regex `Matcher`, and `HttpURLConnection`.

## Control flow, state, and persistence

`calculateDigest()` optionally wraps the provided input stream in an `InputSubstream`, reads 1024-byte chunks, and returns the MD5 digest without closing the caller-owned stream. `createFile()` writes cryptographically random bytes to a sync-on-write random access file and calls `FileDescriptor.sync()` before close. `extractUploadId()` parses the first `<UploadId>...</UploadId>` from XML. `openHttpURLConnection()` sets method and headers, writes an optional body, flushes it, and returns the open connection to the caller.

## Dependencies and integration points

The abstract SDK v1/v2 suites use these helpers for multipart ETag/digest checks, presigned GET/HEAD/PUT/POST/DELETE tests, and file upload inputs. The random-data choice avoids filesystem compression invalidating expected sizes.

## Risks and test signals

The upload ID regex is simple and not namespace-aware; it is suitable for controlled S3 XML responses but not a general XML parser. `openHttpURLConnection()` writes the body before the caller reads status, so request setup failures surface early. Positive signals are correct MD5 ranges for multipart parts, durable random files, upload ID extraction from S3 responses, and successful presigned URL operations.
