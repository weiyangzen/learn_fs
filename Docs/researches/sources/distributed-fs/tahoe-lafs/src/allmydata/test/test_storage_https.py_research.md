# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_storage_https.py

## Purpose
This file tests the TLS-specific part of Tahoe-LAFS HTTP storage, especially SPKI-hash pinning used as a replacement for Foolscap-style server authentication. It validates RFC 7469-style SubjectPublicKeyInfo hashing against test vectors and checks that the HTTP storage HTTPS client policy accepts only the pinned certificate hash while ignoring normal CA validity windows when the pin matches.

## Important APIs, Types, And Helpers
The production APIs are `get_spki`, `get_spki_hash`, `_StorageClientHTTPSPolicy`, and `_TLSEndpointWrapper`. Test infrastructure uses certificate helpers `generate_private_key`, `generate_certificate`, `private_key_to_file`, and `cert_to_file`, plus Twisted `serverFromString`, `Site`, static `Data`, web `Agent`, `HTTPConnectionPool`, `ResponseNeverReceived`, and treq `HTTPClient`.

The test classes are `HTTPSNurlTests` and `PinningHTTPSValidation`. `spki_test_vectors_path` points to `data/spki-hash-test-vectors.yaml`. `PinningHTTPSValidation.listen` is an async context manager that binds a local HTTPS endpoint using the supplied key/certificate, serves a small static body, and stops listening on exit. `request` creates a non-persistent HTTPS treq client using `_StorageClientHTTPSPolicy(expected_spki_hash=...)`.

## Control Flow
`test_spki_hash` loads YAML vector cases, parses PEM certificates with `cryptography.x509`, extracts expected SPKI bytes and URL-safe base64 hashes, and asserts both low-level `get_spki` and higher-level `get_spki_hash` match each vector.

The pinning tests allocate a same-process endpoint, generate private keys and self-signed certificates, write them to temporary files, wrap the endpoint with `_TLSEndpointWrapper.from_paths`, and issue HTTPS GET requests. `test_success` uses the same certificate for server and expected pin and expects the static body. `test_server_certificate_has_wrong_hash` uses one certificate on the server and a different certificate as the expected pin and expects `ResponseNeverReceived`. `test_server_certificate_expired` and `test_server_certificate_not_valid_yet` prove that pin match, not X.509 date validity, controls acceptance.

## State And Persistence Behavior
The tests write temporary private-key and certificate files via `FilePath(self.mktemp())`. The HTTPS server exists only inside the async context manager and is explicitly stopped with `stopListening`; cleanup is followed by `spin_until_cleanup_done` in `tearDown` to avoid dirty reactor state. The client uses a non-persistent `HTTPConnectionPool` so connections are not kept open after each request.

No Tahoe storage shares are persisted here. The persistent artifacts are limited to temporary certificate/key files and the YAML test-vector file read from the source tree.

## Dependencies And Integration Points
This file depends on `cryptography.x509`, PyYAML, Twisted endpoints/web/client, treq, Tahoe certificate-generation test helpers, Tahoe HTTP common TLS hash helpers, and Tahoe HTTP client/server TLS integration. It is the direct integration point between NURL pin material, TLS endpoint wrapping, and the client policy used by HTTP storage.

## Risks And Edge Cases
Covered risks include incorrect SPKI extraction, incorrect URL-safe base64 hash generation, accepting the wrong server certificate, rejecting pinned self-signed certificates because of normal CA validation, rejecting expired/not-yet-valid pinned certificates, and leaking reactor/listening-port resources after TLS tests.

Residual risk includes private-key/certificate mismatch handling. The file notes this is hard to test because OpenSSL refuses to listen with mismatched material. The tests also focus on single-request HTTPS behavior and intentionally avoid persistent connections.

## Test Signals
Passing this file signals that Tahoe-LAFS HTTP storage can authenticate HTTPS servers by SPKI hash, that vector-compatible pin strings are generated, and that TLS validation policy is intentionally pin-based rather than CA/date-based for these storage connections.
