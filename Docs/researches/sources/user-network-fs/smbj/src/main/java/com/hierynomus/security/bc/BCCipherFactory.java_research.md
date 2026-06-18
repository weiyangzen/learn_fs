# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCCipherFactory.java

## Purpose
Bouncy Castle direct cipher factory for DES/ECB/NoPadding and RC4 wrapped behind the project Cipher interface.

## Important APIs / Types / Functions
Defines class `BCCipherFactory` in package `com.hierynomus.security.bc`. Important methods/functions include `create`, `BCBlockCipher`, `createParams`, `BCStreamCipher`, `init`, `update`, `doFinal`, `reset`. Important fields include `lookup`, `wrappedCipher`, `streamCipher`. Source size: 136 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: lookup, wrappedCipher, streamCipher. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.Factory, com.hierynomus.security.Cipher, com.hierynomus.security.SecurityException. JDK/JCE dependencies: java.util.HashMap, java.util.Map. External dependencies: org.bouncycastle.crypto.BufferedBlockCipher, org.bouncycastle.crypto.CipherParameters, org.bouncycastle.crypto.InvalidCipherTextException, org.bouncycastle.crypto.StreamCipher, org.bouncycastle.crypto.engines.DESEngine, org.bouncycastle.crypto.engines.RC4Engine, ... .

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction; legacy NTLM primitives are cryptographically weak but protocol-required for compatibility.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.
