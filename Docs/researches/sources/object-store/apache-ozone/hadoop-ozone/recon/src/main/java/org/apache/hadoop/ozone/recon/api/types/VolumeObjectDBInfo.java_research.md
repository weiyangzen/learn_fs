# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/VolumeObjectDBInfo.java

## Purpose
Volume metadata DTO extending `ObjectDBInfo` with admin, owner, and volume name fields.

## Important APIs, Types, And Functions
declares `VolumeObjectDBInfo`; key fields include `admin`, `owner`, `volume`; important methods include `getAdmin`, `setAdmin`, `getOwner`, `setOwner`, `getVolume`, `setVolume`.

## Control Flow
The `OmVolumeArgs` constructor copies base object fields plus volume-specific admin/owner/name.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover constructor mapping, ACL/base metadata inheritance, and JSON names.
