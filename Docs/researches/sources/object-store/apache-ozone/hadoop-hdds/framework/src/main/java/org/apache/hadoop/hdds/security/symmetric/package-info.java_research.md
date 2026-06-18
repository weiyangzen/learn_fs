# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/package-info.java

## Purpose
This package JavaDoc explains Ozone's symmetric secret-key subsystem for signing and verifying tokens such as block and container tokens.

## Important APIs, Types, And Functions
It points readers to `ManagedSecretKey`, `SecretKeyState`, `SecretKeyStore`, `LocalSecretKeyStore`, and `SecretKeyManager`, and references the HDDS-7733 design.

## Control Flow
There is no executable flow, but the documentation describes the conceptual flow: SCM generates/manages/distributes keys; signers and verifiers use the same key material.

## State, Persistence, And Dependencies
The file has no runtime state. It documents replicated key state and persistent key storage as package concepts.

## Integration Points
The package ties together SCM key lifecycle, OM/SCM token signing, and datanode token verification.

## Risks
The JavaDoc uses HTML tags and an external design link; drift can occur if the implementation evolves beyond the described component set.

## Test Signals
No runtime tests apply, but documentation should stay consistent with package APIs.
