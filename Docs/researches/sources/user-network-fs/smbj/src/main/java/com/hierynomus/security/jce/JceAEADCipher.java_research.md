# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceAEADCipher.java

## Purpose
JCE-backed security adapter. JceAEADCipher wraps platform crypto APIs behind the project interfaces while normalizing provider selection and exception types.

## Important APIs / Types / Functions
Defines class `JceAEADCipher` in package `com.hierynomus.security.jce`. Important methods/functions include `JceAEADCipher`, `init`, `updateAAD`, `update`, `doFinal`, `reset`. Important fields include `cipher`. Source size: 87 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: cipher. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.security.AEADBlockCipher, com.hierynomus.security.Cipher.CryptMode, com.hierynomus.security.SecurityException. JDK/JCE dependencies: java.security.InvalidAlgorithmParameterException, java.security.InvalidKeyException, java.security.NoSuchAlgorithmException, java.security.NoSuchProviderException, java.security.Provider, javax.crypto.BadPaddingException, ... .

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.
