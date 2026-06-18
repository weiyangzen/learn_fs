# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/EntityType.java

## Purpose
Namespace entity discriminator and factory for the handler class that implements root, volume, bucket, directory, key, or unknown-path behavior.

## Important APIs, Types, And Functions
declares `EntityType`; important methods include `create`, `create`, `create`, `create`, `create`, `create`, `create`.

## Control Flow
Each enum constant overrides `create` and wires shared Recon namespace/OM/SCM dependencies into the correct handler implementation.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Recon namespace summary. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover path classification integration, especially `UNKNOWN`, and verify each type returns the expected handler class.
