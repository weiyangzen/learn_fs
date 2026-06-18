# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/OzoneSecretKey.java

## Purpose
`OzoneSecretKey` wraps an asymmetric key pair with Ozone master-key metadata for delegation and block token signing.

## Important APIs, Types, And Functions
The constructor accepts key id, expiry date, `KeyPair`, and certificate serial id. Getters expose key id, expiry, private/public keys, cert serial id, and encoded key bytes. `equals()` and `hashCode()` compare key id, expiry, and key material.

## Control Flow
There is no complex flow: construction validates the key pair, splits it into private/public fields, and accessors return stored values.

## State, Persistence, And Dependencies
State is in-memory private/public key material plus metadata. Persistence is external. Dependencies include Java security keys and Apache Commons builders.

## Integration Points
`OzoneSecretManager` creates and stores the current `OzoneSecretKey` from `CertificateClient` key material and certificate serials. Token secret managers use it to sign identifiers.

## Risks
The method name `getEncodedPubliceKey()` is misspelled but part of current API. `equals()` compares `PrivateKey`/`PublicKey` objects while `hashCode()` uses encoded bytes; provider-specific equality could differ from encoding equality. Certificate serial id is not included in equality/hash.

## Test Signals
Tests should verify construction, encoded key getters, equality/hash behavior across equivalent key pairs, and compatibility with `OzoneSecretManager`.
