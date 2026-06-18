# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/mac/HmacT64.java

## Purpose
Implements the NTLM-specific HMACT64 variant, a modified HMAC-MD5 that truncates long keys rather than hashing them.

## Important APIs / Types / Functions
Defines class `HmacT64` in package `com.hierynomus.security.mac`. Important methods/functions include `HmacT64`, `init`, `doFinal`, `update`, `reset`. Important fields include `BLOCK_LENGTH`, `IPAD`, `OPAD`, `md5`, `ipad`, `opad`. Source size: 112 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: BLOCK_LENGTH, IPAD, OPAD, md5, ipad, opad. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.security.Mac, com.hierynomus.security.MessageDigest, com.hierynomus.security.SecurityException.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.
