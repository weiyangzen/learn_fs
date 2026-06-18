# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/CallerContext.java

## Purpose
Immutable caller-context metadata for RPC audit attribution, with optional signature and thread-local current context.

## Important APIs, Types, And Functions
Main APIs are `getContext`, `getSignature`, `isContextValid`, `toString`, nested `Builder`, `getCurrent`, and `setCurrent`.

## Control Flow
Builder stores context and copies non-empty signature bytes. `toString()` returns empty string for invalid context or `context:signatureAsUtf8` when a signature exists. Static current context uses an `InheritableThreadLocal`.

## State And Persistence
Instances are immutable and defensively copy signatures on build and read. Current context is per-thread inherited state. No persistence.

## Dependencies And Integration Points
Used by IPC scheduling/audit paths and Ozone identity provider tests. Depends on Commons Lang builders for equality/hash and UTF-8 for signature rendering.

## Risks
`hashCode()` only appends context while `equals()` includes signature; this violates the usual hash/equals contract for different signatures with same context. Inheritable thread locals can leak caller context into worker threads if not cleared.

## Test Signals
`TestOzoneIdentityProvider` exercises caller-context extraction. Additional tests should cover signature defensive copy, equals/hash behavior, invalid contexts, and inherited-thread cleanup.
