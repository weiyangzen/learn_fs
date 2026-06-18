# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/security/jce/derivationfunction/KDFCounterHMacSHA256Spec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/security/jce/derivationfunction/KDFCounterHMacSHA256Spec.groovy

Purpose: validates counter-mode HMAC-SHA256 key derivation. The spec instantiates `KDFCounterHMacSHA256` and checks derived bytes for fixed key/label/context/length inputs against known expected output.

State and persistence: no persistent state; all inputs are in-memory byte arrays. Dependencies are JCE HMAC support and SMBJ derivation-function implementation. Integration point is SMB 3.x signing/encryption key derivation. Risks covered include counter placement, label/context concatenation, output truncation, and provider-specific HMAC behavior. Test signal is compact but high-value because a single byte mismatch breaks interoperability.
