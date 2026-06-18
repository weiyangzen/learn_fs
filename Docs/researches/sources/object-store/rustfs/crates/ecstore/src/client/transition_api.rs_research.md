# sources/object-store/rustfs/crates/ecstore/src/client/transition_api.rs

## Purpose
Implements the core S3-compatible transition client: endpoint/TLS setup, credentials, request signing, retrying, URL construction, high-level object/list/multipart wrappers, and common object metadata DTOs.

## Important APIs, types, and functions
Core types are `TransitionClient`, `Options`, `BucketLookupType`, `ReaderImpl`, `RequestMetadata`, `TransitionCore`, `PutObjectPartOptions`, `ObjectInfo`, `RestoreInfo`, `ObjectMultipartInfo`, `UploadInfo`, `SendRequest`, `LocationConstraint`, and `CreateBucketConfiguration`. Key functions include `TransitionClient::new/private_new`, `build_tls_config`, `execute_method`, `new_request`, `doit`, `make_target_url`, `is_virtual_host_style_request`, `hash_materials`, `cred_context`, and `to_object_info`.

## Control flow
Client construction installs or reuses a rustls crypto provider, builds outbound TLS config from global RustFS TLS state, creates a Hyper client, initializes caches/flags/hash algorithms, and applies retry settings. `execute_method` checks offline state, builds signed requests in a retry loop, sends them through `doit`, accepts 200/204/206, parses error bodies, handles some region/cache updates, and retries retryable S3 codes or HTTP statuses. `new_request` resolves bucket location, builds path or virtual-host URL, obtains credentials, supports presigning, injects headers and payload hashes, signs V2/V4 requests, and attaches the body. `TransitionCore` exposes a smaller facade over list, put, multipart, bucket policy, abort, and get-object calls.

## State and persistence behavior
State is process-local: endpoint URL, credentials cache, bucket location cache, trace flags, accelerate/dual-stack flags, hash choices, health status atomics, retry count, and tier type. It does not persist locally; remote object-store state changes through delegated put/list/delete/multipart APIs.

## Dependencies and integration points
It integrates Hyper/Hyper-Rustls, rustls runtime state, RustFS retry utilities, signer crate, checksum modes, put/list/get/multipart modules, bucket location cache, S3 DTOs, UUID/time parsing, and error conversion.

## Risks and edge cases
`doit` converts non-success HTTP responses into generic IO errors, so `execute_method` may not receive structured non-2xx responses for its retry/error parsing. Auto virtual-host mode currently always returns false unless DNS mode is explicitly selected. URL path construction does not percent-encode object path segments. Several behaviors are placeholders or duplicated (`override_signer_type` assignment, tracing methods, health check). `to_object_info` uses simplified parsing for restore/expiration/tags/version IDs.

## Test signals
Unit tests cover rustls panic guarding, TLS config creation not panicking, idempotent provider install, invalid UTF-8 custom header reporting, and signer error mapping. Higher-level behavior is indirectly tested by delete request signing and other client modules.
