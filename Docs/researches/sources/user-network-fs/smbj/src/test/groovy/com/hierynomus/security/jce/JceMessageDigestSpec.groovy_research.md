# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/security/jce/JceMessageDigestSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/security/jce/JceMessageDigestSpec.groovy

Purpose: verifies that `JceSecurityProvider` can load an MD4 message digest from the regular JRE/JDK configuration used by tests. The test constructs the provider and requests MD4 digest support.

State and persistence: no state beyond provider lookup. Dependencies are Java Cryptography Architecture and SMBJ security provider abstraction. Integration point is NTLM hash generation, which needs MD4. Risk covered is missing provider registration or runtime environment incompatibility. Test signal is environment-sensitive and intentionally small; failures point to provider availability rather than algorithm correctness.
