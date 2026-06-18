# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/QuotaUsageResponse.java

## Purpose
Quota usage response exposing allowed quota, used quota, and status.

## Important APIs, Types, And Functions
declares `QuotaUsageResponse`; key fields include `quota`, `quotaUsed`, `responseCode`; important methods include `getQuota`, `getQuotaUsed`, `getResponseCode`, `setQuota`, `setQuotaUsed`, `setResponseCode`.

## Control Flow
Defaults status OK and stores quota values through setters.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover quota exceeded/not-found statuses and byte vs namespace quota producer behavior.
