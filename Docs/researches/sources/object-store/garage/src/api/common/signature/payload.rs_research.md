## sources/object-store/garage/src/api/common/signature/payload.rs

Purpose: verifies standard Authorization-header and presigned-query AWS SigV4 payload signatures and builds canonical request strings.

Important APIs/types/functions: `QueryMap`, `QueryValue`, `CheckedSignature`, `check_payload_signature`, `parse_query_map`, `string_to_sign`, `canonical_request`, `parse_date`, `verify_v4`, and `Authorization::{parse_header, parse_form}` plus private `parse_presigned`.

Control flow: query auth is preferred when `X-Amz-Algorithm` exists; otherwise Authorization header is used; otherwise request is unsigned. Standard auth parses header fields, validates signed headers, canonicalizes request, builds string-to-sign, verifies HMAC, and parses `x-amz-content-sha256`. Presigned auth excludes `X-Amz-Signature` from canonical query, validates expiry up to 7 days, verifies HMAC, and injects signed `x-amz-*` query values as headers while detecting signed header/query conflicts.

State/persistence: reads local key table, rejects deleted or expired keys, and reads configured S3 region. Does not mutate.

Dependencies/integration: core of S3/K2V auth. Uses `uri_encode`, Garage key params, table lookup, chrono, hmac, sha256, and hyper headers.

Risks: canonicalization is subtle: S3 avoids double URI encoding while other services encode differently; paths are not normalized. Date freshness is enforced for 24h header auth and query expiry for presigned URLs. Duplicate query parameters are rejected because `HeaderMap` stores one value.

Test signals: no local tests in this file; must be exercised by SigV4 compatibility tests and AWS/minio client interop.
