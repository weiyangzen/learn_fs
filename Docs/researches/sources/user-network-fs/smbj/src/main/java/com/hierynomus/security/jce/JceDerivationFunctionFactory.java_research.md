# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceDerivationFunctionFactory.java

## Purpose
JCE-backed security adapter. JceDerivationFunctionFactory wraps platform crypto APIs behind the project interfaces while normalizing provider selection and exception types.

## Important APIs / Types / Functions
Defines class `JceDerivationFunctionFactory` in package `com.hierynomus.security.jce`. Important methods/functions include `create`. Important fields include `lookup`. Source size: 53 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: lookup. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.Factory, com.hierynomus.security.DerivationFunction, com.hierynomus.security.jce.derivationfunction.KDFCounterHMacSHA256. JDK/JCE dependencies: java.security.NoSuchAlgorithmException, java.util.HashMap, java.util.Map.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.
