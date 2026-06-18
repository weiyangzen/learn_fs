# sources/object-store/garage/src/garage/tests/s3/multipart.rs

Purpose: This file tests multipart upload lifecycle, checksummed multipart parts, part listing pagination, completion cleanup, `GetObject` by part number, and `UploadPartCopy` from single-part and multipart source objects.

Important APIs and types: Tests are `test_multipart_upload`, `test_multipart_with_checksum`, `test_uploadlistpart`, and `test_uploadpartcopy`. They use AWS SDK `create_multipart_upload`, `upload_part`, `list_parts`, `complete_multipart_upload`, `head_object`, `get_object`, `upload_part_copy`, `ChecksumAlgorithm::Sha1`, `CompletedMultipartUpload`, `CompletedPart`, and helper `calculate_sha1`.

Control flow: The basic test uploads parts out of order, overwrites part 1, completes with selected parts, confirms the upload is gone, checks final length, full body, and per-part reads. The checksum test starts a SHA1 MPU, rejects a wrong part checksum, validates listed part checksums, computes the multipart checksum-of-checksums, and verifies completion response. The list-part test checks empty lists, ordering, ETags, sizes, pagination markers, and final completion. The copy test builds source objects, copies byte ranges from them into target MPU parts, completes, and verifies exact concatenated bytes.

State and persistence behavior: The tests persist multipart upload metadata, individual part bodies, checksums, final object versions, and source objects. Completion should remove upload state and publish the assembled object.

Dependencies and integration points: They cover Garage's multipart metadata tables, block/object storage, checksum validation, range copy handling, S3 XML/SDK response mapping, and object read path.

Risks: Payloads are 5-10 MiB and can be slow or memory-heavy. Exact ETags assume MD5 behavior for the fixed data. The tests do not cover abort MPU or invalid completion ordering/error cases beyond checksum rejection.

Test signals: Upload IDs, part counts, expected ETags, checksum fields, wrong checksum failure, content lengths, object body equality, list-parts pagination fields, upload disappearance after completion, and exact assembled copy output.
