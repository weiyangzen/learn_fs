# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/token/TestContainerTokenVerifier.java

## Purpose

This class specializes the abstract token-verifier test matrix for `ContainerTokenVerifier`.

## Important APIs, Types, And Functions

It overrides token fixture methods for `HDDS_CONTAINER_TOKEN_ENABLED`, `ContainerTokenVerifier`, `ContainerTokenIdentifier`, create-container requests, and write-chunk requests. `AtomicLong CONTAINER_ID` gives each token/request a unique container ID.

## Control Flow

Inherited tests build token-enabled/disabled configs and verify behavior. For container tokens, write-chunk is treated as unrelated/unverified, while create-container requires a token for the incremented container ID.

## State And Persistence

State is in-memory token IDs and an atomic counter. There is no persistence.

## Dependencies And Integration Points

It integrates container-token verification with datanode container command classification, `ContainerID`, and the shared token verifier test base.

## Risks

The atomic counter is static, so generated IDs increase across test invocations. This is useful for uniqueness but can surprise tests that assume fixed IDs.

## Test Signals

Signals are the inherited token verifier matrix applied to container-token-specific commands and identifiers.
