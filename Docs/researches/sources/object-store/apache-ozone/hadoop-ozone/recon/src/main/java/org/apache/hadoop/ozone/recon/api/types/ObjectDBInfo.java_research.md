# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ObjectDBInfo.java

## Purpose
Base object metadata DTO for namespace responses with metadata map, name, quotas, used namespace, creation/modification times, and ACLs.

## Important APIs, Types, And Functions
declares `ObjectDBInfo`; key fields include `metadata`, `name`, `quotaInBytes`, `quotaInNamespace`, `usedNamespace`, `creationTime`, `modificationTime`, `acls`; important methods include `getMetadata`, `getName`, `getQuotaInBytes`, `getQuotaInNamespace`, `getUsedNamespace`, `getCreationTime`, `getModificationTime`, `getAcls`.

## Control Flow
Constructors can populate common fields from OM directory or prefix info; subclasses add volume/bucket-specific data.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover directory/prefix constructor mapping, ACL serialization, and quota sentinel values.
