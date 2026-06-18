# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/x509/keys/TestKeyCodec.java

## Purpose
Tests PEM/DER-style key encoding and decoding behavior in `KeyCodec`.

## Important APIs, types, and functions
- Uses `KeyCodec`, `SecurityConstants`, `KeyPairGenerator`, and Java `KeyPair` APIs.
- Covers unknown encoding failure and parameterized public/private key encode-decode round trips for configured encodings.

## Control flow
The tests generate RSA keys, encode public or private keys through the codec, decode the bytes back, and assert equality with the original key. An invalid encoding path asserts exception behavior.

## State and persistence behavior
All key material is in memory. Encoded byte arrays represent persisted key-file payloads but are not necessarily written to disk here.

## Dependencies and integration points
`KeyCodec` is used by `KeyStorage` and security bootstrap code to read/write key files.

## Risks and test signals
Encoding drift can make existing key files unreadable. These tests signal compatibility for supported encodings and fail-fast behavior for invalid encodings.
