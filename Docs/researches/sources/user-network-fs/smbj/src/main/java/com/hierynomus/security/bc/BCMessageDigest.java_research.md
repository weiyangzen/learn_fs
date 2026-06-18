# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCMessageDigest.java

## Purpose
Direct Bouncy Castle security adapter. BCMessageDigest maps project-level algorithm names to Bouncy Castle digest, MAC, cipher, AEAD, or KDF implementations.

## Important APIs / Types / Functions
Defines class `BCMessageDigest` in package `com.hierynomus.security.bc`. Important methods/functions include `create`, `BCMessageDigest`, `getDigest`, `update`, `digest`, `reset`, `getDigestLength`. Important fields include `lookup`, `digest`. Source size: 105 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: lookup, digest. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.Factory, com.hierynomus.security.MessageDigest. JDK/JCE dependencies: java.util.HashMap, java.util.Map. External dependencies: org.bouncycastle.crypto.Digest, org.bouncycastle.crypto.digests.MD4Digest, org.bouncycastle.crypto.digests.MD5Digest, org.bouncycastle.crypto.digests.SHA256Digest, org.bouncycastle.crypto.digests.SHA512Digest.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction; legacy NTLM primitives are cryptographically weak but protocol-required for compatibility.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.
