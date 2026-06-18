# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCSecurityProvider.java

## Purpose
SecurityProvider implementation backed by direct Bouncy Castle primitives and the local HMACT64 adapter.

## Important APIs / Types / Functions
Defines class `BCSecurityProvider` in package `com.hierynomus.security.bc`. Important methods/functions include `getDigest`, `getMac`, `getCipher`, `getAEADBlockCipher`, `getDerivationFunction`. Source size: 61 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.security.AEADBlockCipher, com.hierynomus.security.Cipher, com.hierynomus.security.DerivationFunction, com.hierynomus.security.Mac, com.hierynomus.security.MessageDigest, com.hierynomus.security.SecurityProvider, ... . JDK/JCE dependencies: java.util.Objects.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.
