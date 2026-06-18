# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/messagedigest/MD4.java

## Purpose
Pure Java MD4 MessageDigest fallback used when the active JCE provider does not supply MD4.

## Important APIs / Types / Functions
Defines class `MD4` in package `com.hierynomus.security.jce.messagedigest`. Important methods/functions include `MD4`, `engineGetDigestLength`, `engineUpdate`, `engineDigest`, `engineReset`, `pad`, `process`. Important fields include `BYTE_DIGEST_LENGTH`, `BYTE_BLOCK_LENGTH`, `A`, `B`, `C`, `D`, `a`, `b`, `c`, `d`, `msgLength`, `buffer`. Source size: 314 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: BYTE_DIGEST_LENGTH, BYTE_BLOCK_LENGTH, A, B, C, D, a, b, c, d, msgLength, buffer. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
JDK/JCE dependencies: java.security.DigestException, java.security.MessageDigest.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction; legacy NTLM primitives are cryptographically weak but protocol-required for compatibility.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.
