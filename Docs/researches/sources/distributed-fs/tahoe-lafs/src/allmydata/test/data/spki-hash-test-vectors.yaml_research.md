<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/data/spki-hash-test-vectors.yaml -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/data/spki-hash-test-vectors.yaml

Purpose: Stores certificate/SPKI hash fixtures used to verify SubjectPublicKeyInfo extraction and hash encoding behavior.

Important data shape: The top-level `vector` list contains entries with `expected-hash`, `expected-spki`, and PEM `certificate` fields. Vectors include RSA public keys of different sizes and an Ed25519-style key, giving coverage for multiple key algorithms and DER encodings.

Control flow: This YAML file has no executable control flow. Tests load it, parse each certificate, extract SPKI DER, compare it with `expected-spki`, and compare the derived hash with `expected-hash`.

State and persistence: Static test data only; no runtime mutation. Certificates are fixtures and not trusted operational credentials.

Dependencies and integration points: Consumed by crypto/certificate tests, likely through YAML parsing and cryptography/OpenSSL primitives for certificate loading and SPKI derivation. The base64/base64url fields must stay compatible with those consumers.

Risks: Fixture correctness is binary: a typo in line wrapping, padding, or PEM indentation can break parsing or mask hash regressions. Certificates may be expired, but expiration should be irrelevant for SPKI extraction tests.

Test signals: Confirm all vectors parse, extracted DER equals `expected-spki`, hash encoding equals `expected-hash`, and test logic ignores certificate validity periods while still rejecting malformed fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/data/spki-hash-test-vectors.yaml -->
