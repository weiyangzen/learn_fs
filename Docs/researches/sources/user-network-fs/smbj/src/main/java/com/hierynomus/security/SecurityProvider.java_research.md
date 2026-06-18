# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/SecurityProvider.java

## Purpose
Abstraction boundary for digest, MAC, cipher, AEAD cipher, and derivation-function implementations.

## Important APIs / Types / Functions
Defines interface `SecurityProvider` in package `com.hierynomus.security`. Source size: 40 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Dependencies are limited to same-package language constructs and no explicit imports.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.
