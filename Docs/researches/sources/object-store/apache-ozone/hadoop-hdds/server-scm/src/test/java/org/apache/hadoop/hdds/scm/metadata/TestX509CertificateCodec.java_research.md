# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/metadata/TestX509CertificateCodec.java

Purpose: compatibility test for persisted SCM metadata `X509CertificateCodec`, comparing the current codec with the legacy PEM codec across multiple RSA key sizes.

Important APIs and types: `oldCodec = OldX509CertificateCodecForTesting.get()` and `newCodec = X509CertificateCodec.get()`. `genKeyPair(String,int)` creates RSA key pairs with a specified size. `initSecurityConfig()` initializes Ozone security providers. `testRSA()` runs `runTestRSA()` for key sizes 512, 1024, 2048, and 4096. Each run generates a self-signed certificate with `KeyStoreTestUtil.generateCertificate(...)` and uses `CodecTestUtil.runTest(newCodec, x509, null, oldCodec)`.

Control flow: generated certificates vary in key size and random validity duration. The test prints the PEM string, then exercises new codec serialization, deserialization, copying/buffer paths, and old-codec compatibility through the utility.

State and persistence: no database is opened. Persisted state is represented as certificate bytes, with the old codec modeling PEM UTF-8. Dependencies include Java crypto, Ozone security provider setup, `CertificateCodec`, and HDDS codec testing utilities.

Integration points and risks: guards SCM certificate table upgrade compatibility. Environmental risks include crypto provider availability and slower large-key generation. It does not test non-RSA certificates, malformed bytes, certificate chains, or security policy around expired certificates.
