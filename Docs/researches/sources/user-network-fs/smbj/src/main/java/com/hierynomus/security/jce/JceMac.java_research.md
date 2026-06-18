# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceMac.java

## Purpose
JCE-backed security adapter. JceMac wraps platform crypto APIs behind the project interfaces while normalizing provider selection and exception types.

## Important APIs / Types / Functions
Defines class `JceMac` in package `com.hierynomus.security.jce`. Important methods/functions include `JceMac`, `init`, `update`, `doFinal`, `reset`. Important fields include `algorithm`, `mac`. Source size: 79 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: algorithm, mac. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.security.Mac, com.hierynomus.security.SecurityException. JDK/JCE dependencies: javax.crypto.spec.SecretKeySpec, java.security.InvalidKeyException, java.security.NoSuchAlgorithmException, java.security.NoSuchProviderException, java.security.Provider.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.
