# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/derivationfunction/KDFCounterHMacSHA256.java

## Purpose
JCE implementation of counter-mode HMAC-SHA256 derivation used by SMB signing/encryption key derivation flows.

## Important APIs / Types / Functions
Defines class `KDFCounterHMacSHA256` in package `com.hierynomus.security.jce.derivationfunction`. Important methods/functions include `KDFCounterHMacSHA256`, `init`, `generateBytes`. Important fields include `mac`, `fixedSuffix`, `maxLength`. Source size: 80 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: mac, fixedSuffix, maxLength. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.security.SecurityException, com.hierynomus.security.jce.JceDerivationFunction. JDK/JCE dependencies: java.security.InvalidKeyException, java.security.NoSuchAlgorithmException, javax.crypto.Mac, javax.crypto.spec.SecretKeySpec.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.
