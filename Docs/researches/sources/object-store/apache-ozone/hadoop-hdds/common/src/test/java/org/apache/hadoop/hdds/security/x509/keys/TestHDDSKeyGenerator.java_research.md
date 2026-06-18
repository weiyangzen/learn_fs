# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/x509/keys/TestHDDSKeyGenerator.java

## Purpose
Tests RSA key generation through `HDDSKeyGenerator` and `SecurityConfig`.

## Important APIs, types, and functions
- Uses `OzoneConfiguration`, `SecurityConfig`, `HDDSKeyGenerator`, `KeyPair`, `PublicKey`, `RSAPublicKey`, and `PKCS8EncodedKeySpec`.
- Test cases are `testGenerateKey` and `testGenerateKeyWithSize`.
- Initializes temporary security paths with `@TempDir`.

## Control flow
Setup configures security-related base directories, then tests generate key pairs with default and configured sizes and assert algorithm/type/bit-length properties.

## State and persistence behavior
Key pairs are generated in memory. Temporary directory configuration is present but this generator test does not validate persistent key storage.

## Dependencies and integration points
The generator feeds HDDS certificate/key storage and CA initialization flows.

## Risks and test signals
Wrong algorithms or key sizes weaken TLS and certificate behavior. The test signals that configured RSA key size is honored.
