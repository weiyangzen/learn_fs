# sources/object-store/garage/src/garage/tests/s3/objects.rs

Purpose: This file tests core S3 object operations: PUT, GET, HEAD metadata, conditional reads, byte ranges, response header overrides, custom metadata, Unicode/control-character keys, and object deletion.

Important APIs and types: Tests are `test_putobject`, `test_precondition`, `test_getobject`, `test_metadata`, and `test_deleteobject`. They use AWS SDK `put_object`, `get_object`, `head_object`, `delete_object`, `delete_objects`, byte streams, `SdkError`, `DateTime`, `Delete`, and `ObjectIdentifier`.

Control flow: `test_putobject` uploads empty and non-empty objects under ordinary, control-character, and Unicode keys and verifies ETags/content metadata. `test_precondition` validates `If-Match`, `If-None-Match`, `If-Modified-Since`, and `If-Unmodified-Since` status behavior. `test_getobject` checks three byte-range forms. `test_metadata` verifies stored headers/metadata and response overrides. `test_deleteobject` uploads ten objects, deletes two individually and eight in batch, verifies empty listing, and tolerates deleting a missing key.

State and persistence behavior: The tests persist object versions, content bytes, user metadata, HTTP metadata, last-modified timestamps, and delete markers/state sufficient for list results to become empty.

Dependencies and integration points: They exercise the S3 object API, metadata storage, range reader, conditional request evaluator, multi-delete handling, key encoding, and AWS SDK error mapping.

Risks: Some comments note Garage behavior around version IDs differs or is not compared to AWS. Exact ETags are tied to MD5 of known payloads. Timestamp comparisons use derived seconds and assume stable server rounding behavior.

Test signals: Exact ETags, content lengths, body bytes, content types, last-modified presence, status 304/412 for preconditions, exact content-range headers, metadata round-trips including Unicode metadata, deleted count 8, empty list after deletion, and successful delete of a non-existent object.
