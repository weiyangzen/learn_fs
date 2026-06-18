# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/MessageDigest.java

## Purpose
Security abstraction type. MessageDigest defines the project-facing contract used by NTLM and SMB cryptographic code without binding callers to JCE or Bouncy Castle.

## Important APIs / Types / Functions
Defines interface `MessageDigest` in package `com.hierynomus.security`. Source size: 30 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Dependencies are limited to same-package language constructs and no explicit imports.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.
