# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/UsedSpaceBreakDown.java

## Purpose
Used-space breakdown for utilization APIs, separating open-key bytes from finalized key bytes.

## Important APIs, Types, And Functions
declares `UsedSpaceBreakDown`; key fields include `openKeyBytes`, `finalizedKeyBytes`; important methods include `getOpenKeyBytes`, `getFinalizedKeyBytes`.

## Control Flow
Constructor-only composition of `OpenKeyBytesInfo` and finalized-byte total.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should verify aggregate sums and open/finalized split from OM tables.
