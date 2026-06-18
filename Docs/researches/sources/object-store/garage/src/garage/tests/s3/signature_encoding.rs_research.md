# sources/object-store/garage/src/garage/tests/s3/signature_encoding.rs

Purpose: This test verifies that Garage's SigV4 verification accepts equivalent URI percent-encoding forms for special characters in presigned URLs.

Important APIs and types: `test_signature_encoding` uses AWS SDK `put_object`, `get_object`, presigning, Hyper `Request`, `StatusCode`, and manual URI string replacement.

Control flow: The test uploads and reads an object with key `key@good~.txt`, presigns a GET, alters the generated URL by replacing `%40` with `@` and `~` with `%7E`, sends the modified request with the original signed headers, and expects 200 OK.

State and persistence behavior: It persists one object and tests signature verification against a modified request URI that should be canonically equivalent.

Dependencies and integration points: It exercises object key encoding, AWS SDK presigning, Garage canonical URI normalization, and Hyper request execution.

Risks: It covers only two character transformations and one key. The altered URL remains semantically equivalent; it does not test invalid encodings or double-encoding attacks.

Test signals: Successful upload/read control path and 200 OK for the altered presigned URL.
