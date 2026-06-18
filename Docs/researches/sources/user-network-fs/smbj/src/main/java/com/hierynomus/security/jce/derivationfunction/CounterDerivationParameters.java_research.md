# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/derivationfunction/CounterDerivationParameters.java

## Purpose
JCE-backed security adapter. CounterDerivationParameters wraps platform crypto APIs behind the project interfaces while normalizing provider selection and exception types.

## Important APIs / Types / Functions
Defines class `CounterDerivationParameters` in package `com.hierynomus.security.jce.derivationfunction`. Important methods/functions include `CounterDerivationParameters`, `getSeed`, `getFixedCounterSuffix`, `getCounterLength`. Important fields include `seed`, `fixedCounterSuffix`, `counterLength`. Source size: 53 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: seed, fixedCounterSuffix, counterLength. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
JDK/JCE dependencies: java.util.Arrays.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.
