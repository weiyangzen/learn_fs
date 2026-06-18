# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCDerivationFunctionFactory.java

## Purpose
Bouncy Castle direct counter-mode KDF factory for KDF/Counter/HMACSHA256.

## Important APIs / Types / Functions
Defines class `BCDerivationFunctionFactory` in package `com.hierynomus.security.bc`. Important methods/functions include `create`, `BCDerivationFunction`, `createParams`, `init`, `generateBytes`. Important fields include `lookup`, `function`. Source size: 79 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: lookup, function. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.Factory, com.hierynomus.security.DerivationFunction, com.hierynomus.security.jce.derivationfunction.CounterDerivationParameters, com.hierynomus.security.jce.derivationfunction.DerivationParameters. JDK/JCE dependencies: java.util.HashMap, java.util.Map. External dependencies: org.bouncycastle.crypto.digests.SHA256Digest, org.bouncycastle.crypto.generators.KDFCounterBytesGenerator, org.bouncycastle.crypto.macs.HMac, org.bouncycastle.crypto.params.KDFCounterParameters.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.
