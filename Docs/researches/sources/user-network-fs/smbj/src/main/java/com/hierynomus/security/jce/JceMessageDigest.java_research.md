# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceMessageDigest.java

## Purpose
JCE-backed security adapter. JceMessageDigest wraps platform crypto APIs behind the project interfaces while normalizing provider selection and exception types.

## Important APIs / Types / Functions
Defines class `JceMessageDigest` in package `com.hierynomus.security.jce`. Important methods/functions include `JceMessageDigest`, `update`, `digest`, `reset`, `getDigestLength`. Important fields include `md`. Source size: 79 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: md. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.security.MessageDigest, com.hierynomus.security.SecurityException, com.hierynomus.security.jce.messagedigest.MD4. JDK/JCE dependencies: java.security.NoSuchAlgorithmException, java.security.NoSuchProviderException, java.security.Provider.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction; legacy NTLM primitives are cryptographically weak but protocol-required for compatibility.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.
