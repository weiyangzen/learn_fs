# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCAEADCipherFactory.java

## Purpose
Bouncy Castle direct AEAD factory for AES/CCM/NoPadding and AES/GCM/NoPadding wrapped in the project AEADBlockCipher interface.

## Important APIs / Types / Functions
Defines class `BCAEADCipherFactory` in package `com.hierynomus.security.bc`. Important methods/functions include `create`, `BCAEADBlockCipher`, `createParams`, `init`, `updateAAD`, `update`, `doFinal`, `reset`. Important fields include `lookup`, `wrappedCipher`. Source size: 128 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: lookup, wrappedCipher. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.Factory, com.hierynomus.security.AEADBlockCipher, com.hierynomus.security.Cipher.CryptMode, com.hierynomus.security.SecurityException. JDK/JCE dependencies: java.util.HashMap, java.util.Map, javax.crypto.spec.GCMParameterSpec. External dependencies: org.bouncycastle.crypto.CipherParameters, org.bouncycastle.crypto.InvalidCipherTextException, org.bouncycastle.crypto.engines.AESEngine, org.bouncycastle.crypto.modes.CCMBlockCipher, org.bouncycastle.crypto.modes.GCMBlockCipher, org.bouncycastle.crypto.params.AEADParameters, ... .

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.
