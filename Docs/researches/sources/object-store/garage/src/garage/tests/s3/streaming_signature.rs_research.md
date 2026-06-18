# sources/object-store/garage/src/garage/tests/s3/streaming_signature.rs

Purpose: This file tests AWS SigV4 streaming upload modes against S3 operations, including signed chunked payloads, unsigned payload trailers, trailer checksum validation, streaming bucket creation, and streaming website configuration upload.

Important APIs and types: Tests use `CustomRequester`, `BodySignature::Streaming`, `BodySignature::StreamingUnsignedTrailer`, CRC32 from `crc_fast`, base64 encoding, Hyper `Method`, CLI key permission helper, and AWS SDK reads/checksum mode.

Control flow: `test_putobject_streaming` uploads an empty object and a checksum-bearing object through signed streaming chunks, then reads them with the SDK. `test_putobject_streaming_unsigned_trailer` uploads empty and non-empty objects with unsigned trailer checksums, first verifying a wrong checksum fails. `test_create_bucket_streaming` grants create-bucket and creates a bucket using a streaming request body, then verifies object operations work. `test_put_website_streaming` sends XML website configuration in a streaming PUT with `?website` and verifies the stored config through the SDK.

State and persistence behavior: The tests persist objects, checksums, a created bucket, and website configuration. The key state is request-body decoding and checksum/signature verification before data is committed.

Dependencies and integration points: They integrate Garage SigV4 streaming parser, checksum validation, object storage, bucket creation authorization, website configuration parsing, and the custom request builder.

Risks: The custom requester cannot currently URL-encode control-character paths, noted in comments. Streaming body generation is test-only and may not represent all client implementations. Wrong trailer checksum is checked only as a generic client error.

Test signals: Successful streaming PUTs, failed wrong trailer checksum, exact object bytes, ETags, content length, stored CRC32 checksum, successful streaming bucket creation, and website config fields `home.html` and `err/error.html`.
