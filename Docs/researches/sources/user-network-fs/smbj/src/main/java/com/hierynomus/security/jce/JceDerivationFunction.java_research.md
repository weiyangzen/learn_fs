# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceDerivationFunction.java

## Purpose
JCE-backed security adapter. JceDerivationFunction wraps platform crypto APIs behind the project interfaces while normalizing provider selection and exception types.

## Important APIs / Types / Functions
Defines class `JceDerivationFunction` in package `com.hierynomus.security.jce`. Important methods/functions include `init`, `generateBytes`. Source size: 33 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.security.DerivationFunction, com.hierynomus.security.SecurityException, com.hierynomus.security.jce.derivationfunction.DerivationParameters.

## Risks and Edge Cases
some API surface intentionally throws unsupported/TODO behavior and callers need explicit coverage; mutable byte arrays can be modified by callers after construction.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.
