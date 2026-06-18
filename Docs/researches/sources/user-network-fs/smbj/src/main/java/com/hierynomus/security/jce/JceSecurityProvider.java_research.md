# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceSecurityProvider.java

## Purpose
SecurityProvider implementation backed by the configured JCE provider, provider name, or platform default.

## Important APIs / Types / Functions
Defines class `JceSecurityProvider` in package `com.hierynomus.security.jce`. Important methods/functions include `JceSecurityProvider`, `getDigest`, `getMac`, `getCipher`, `getAEADBlockCipher`, `getDerivationFunction`. Important fields include `jceProvider`, `providerName`. Source size: 71 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: jceProvider, providerName. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.security.*, com.hierynomus.security.SecurityException, com.hierynomus.security.mac.HmacT64. JDK/JCE dependencies: java.security.Provider, java.util.Objects.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.
