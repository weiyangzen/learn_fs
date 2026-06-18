# sources/object-store/garage/src/garage/tests/s3/presigned.rs

Purpose: This file tests presigned S3 request compatibility, including normal PUT/GET and canonical header whitespace normalization for user metadata.

Important APIs and types: `test_presigned_url` and `test_presigned_put_with_user_metadata` use AWS SDK `PresigningConfig`, Hyper `Request`, `Bytes`, `Full`, and the shared custom Hyper client.

Control flow: The first test creates a presigning config with a start time in the past, presigns PUT and GET for one key, executes them through Hyper without SDK send logic, checks status/ETag, and verifies body bytes. The second test presigns a PUT with metadata value containing internal sequential spaces, copies presigned headers into a Hyper request, sends it, and expects 200.

State and persistence behavior: The tests persist one ordinary object and one metadata-bearing object through presigned requests. The key state is Garage's SigV4 validation of query-signed URLs and canonical request construction.

Dependencies and integration points: They bridge AWS SDK presigning, Garage signature verification, Hyper execution, object PUT/GET, ETag generation, and metadata header canonicalization.

Risks: The tests do not cover expired URLs, wrong signatures, signed payload hashes, or all response override parameters. They rely on current SDK presigner behavior for URL/header construction.

Test signals: HTTP 200 from Hyper-executed presigned PUT/GET, expected ETag, exact GET body, and acceptance of metadata headers with collapsible whitespace.
