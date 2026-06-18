# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ScmPendingDeletion.java

## Purpose
Aggregate SCM pending deletion metrics: logical block size, replicated block size, and block count.

## Important APIs, Types, And Functions
declares `ScmPendingDeletion`; key fields include `totalBlocksize`, `totalReplicatedBlockSize`, `totalBlocksCount`; important methods include `getTotalBlocksize`, `getTotalReplicatedBlockSize`, `getTotalBlocksCount`.

## Control Flow
Constructor-only DTO with Jackson properties populated by SCM deletion accounting endpoints.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should verify replicated-vs-logical byte calculations and count consistency.
