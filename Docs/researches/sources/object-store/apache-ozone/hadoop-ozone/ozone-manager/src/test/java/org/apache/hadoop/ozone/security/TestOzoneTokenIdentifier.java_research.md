<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/TestOzoneTokenIdentifier.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/TestOzoneTokenIdentifier.java

Purpose: JUnit 5 coverage for `OzoneTokenIdentifier` signing, serialization, URL token encoding, and persisted codec compatibility. It verifies that token identity fields survive Hadoop `Writable` and `Token` round trips and that `TokenIdentifierCodec` can read current persisted bytes with and without an OM service id.

Important APIs and functions: `testSignToken`, `signTokenAsymmetric`, `verifyTokenAsymmetric`, `signTokenSymmetric`, `generateTestToken`, `testAsymmetricTokenPerf`, `testSymmetricTokenPerf`, `testReadWriteInProtobuf`, `testTokenSerialization`, and parameterized `testTokenPersistence`. The helper `getIdentifierInst` builds a representative identifier with owner, renewer, issue/max dates, sequence number, and OM cert serial id.

Control flow: asymmetric tests create a temporary keystore/truststore, generate an RSA key pair and certificate, sign `tokenId.getBytes()`, and verify the signature with the certificate. Serialization tests write the identifier through `DataOutputStream`, read via `readFields`, encode a Hadoop `Token` to URL form, decode it, then deserialize the embedded identifier.

State and persistence behavior: test state is local to temp directories and byte arrays. Persistence risk is centered on `OzoneTokenIdentifier.getBytes()`, protobuf/writable wire format, optional `omServiceId`, and `TokenIdentifierCodec.fromPersistedFormat`.

Dependencies and integration: Java crypto (`Signature`, `Mac`, `KeyGenerator`), Hadoop `Text` and `Token`, `KeyStoreTestUtil`, Ozone `TokenIdentifierCodec`, and JUnit temp dirs/parameterized tests. Risk areas include cryptographic algorithm availability, token equality including time fields, and backward compatibility of persisted token bytes. Test signals are positive round-trip equality checks; performance tests only log timings and do not assert thresholds.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/TestOzoneTokenIdentifier.java -->
