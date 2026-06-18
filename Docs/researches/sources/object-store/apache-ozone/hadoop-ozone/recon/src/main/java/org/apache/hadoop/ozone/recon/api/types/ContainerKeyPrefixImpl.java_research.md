# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerKeyPrefixImpl.java

## Purpose
Package-private immutable implementation shared by `ContainerKeyPrefix` and `KeyPrefixContainer` to represent both lookup directions in Recon container DB indexes.

## Important APIs, Types, And Functions
declares `ContainerKeyPrefixImpl`; key fields include `containerId`, `keyPrefix`, `keyVersion`; important methods include `getContainerId`, `getKeyPrefix`, `getKeyVersion`, `toContainerKeyPrefix`, `toKeyPrefixContainer`, `hashCode`, `equals`.

## Control Flow
Stores container id, key prefix, and key version; conversion to `KeyPrefixContainer` returns null when the key prefix is absent or empty.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are null handling in `hashCode` for container-only keys, equality assumptions across interface views, and callers expecting conversion to always return a key-prefix object.

## Test Signals
Tests should cover equality, conversion, and the null-prefix hashCode risk because `hashCode` calls `keyPrefix.hashCode()` while container-only keys are allowed.
