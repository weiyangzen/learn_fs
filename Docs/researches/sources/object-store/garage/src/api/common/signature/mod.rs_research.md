## sources/object-store/garage/src/api/common/signature/mod.rs

Purpose: top-level AWS SigV4 signature module and public entry point for authenticated request verification.

Important APIs/types/functions: submodules `body`, `checksum`, `error`, `payload`, `streaming`; constants for SigV4 date/header names and streaming modes; `ContentSha256Header`; `VerifiedRequest`; `verify_request`; `signing_hmac`; `compute_scope`.

Control flow: `verify_request` calls `payload::check_payload_signature`, wraps the incoming body with `streaming::parse_streaming_body`, requires an authenticated key, and returns `Request<ReqBody>` plus access key and content-sha256 mode. `signing_hmac` derives the SigV4 signing key through date, region, service, and `aws4_request`.

State/persistence: reads Garage config region and key table via payload verification; no mutations.

Dependencies/integration: used by S3 and K2V servers with service names `s3` and `k2v`. Depends on Garage model key table and crypto HMAC/SHA256.

Risks: anonymous access is currently rejected after body wrapping decision. Region/service scope must match clients exactly. Any bug here affects authentication for multiple APIs.

Test signals: no local tests in this root; payload and streaming behavior is partially tested in submodules and integration clients.
