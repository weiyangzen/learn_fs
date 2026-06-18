# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/keys/KeyCodec.java

## Purpose
Encodes and decodes public/private keys in PEM format using RFC-7468-compatible ASCII text and Java key factories.

## Important APIs and types
The constructor creates a `KeyFactory` for the configured algorithm. `encodePublicKey` and `encodePrivateKey` wrap key bytes in Bouncy Castle `PemObject`s with `PUBLIC KEY` or `PRIVATE KEY` labels. `decodePrivateKey` and `decodePublicKey` parse a PEM object and generate Java key instances.

## Control flow and state
The only state is the `KeyFactory`. Encoding writes ASCII PEM through `PemWriter`. Decoding reads one PEM object, wraps content in `PKCS8EncodedKeySpec`, and applies a generator function. Public key decoding adapts the content into an `X509EncodedKeySpec` for `generatePublic`.

## Dependencies and integration points
Uses `SecurityConstants` PEM labels, Bouncy Castle PEM reader/writer, Java key specs, and Ratis `CheckedFunction`. `SecurityConfig.keyCodec()` and `KeyStorage` use it for key persistence.

## Risks and test signals
Tests should cover private/public round trips for configured algorithms, invalid PEM, mismatched algorithm, empty input, and compatibility with existing key files. The decode helper assumes `readPemObject()` returns non-null and that public-key content can be represented from the PKCS8 wrapper; malformed inputs can produce null dereferences or `IOException`.
