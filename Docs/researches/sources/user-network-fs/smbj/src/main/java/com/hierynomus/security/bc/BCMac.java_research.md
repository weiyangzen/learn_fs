# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCMac.java

## Purpose
Direct Bouncy Castle security adapter. BCMac maps project-level algorithm names to Bouncy Castle digest, MAC, cipher, AEAD, or KDF implementations.

## Important APIs / Types / Functions
Defines class `BCMac` in package `com.hierynomus.security.bc`. Important methods/functions include `create`, `BCMac`, `getMacFactory`, `init`, `update`, `doFinal`, `reset`. Important fields include `lookup`, `mac`. Source size: 100 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: lookup, mac. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.Factory, com.hierynomus.security.Mac. JDK/JCE dependencies: java.util.HashMap, java.util.Map. External dependencies: org.bouncycastle.crypto.digests.MD5Digest, org.bouncycastle.crypto.digests.SHA256Digest, org.bouncycastle.crypto.engines.AESEngine, org.bouncycastle.crypto.macs.CMac, org.bouncycastle.crypto.macs.HMac, org.bouncycastle.crypto.params.KeyParameter.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.
