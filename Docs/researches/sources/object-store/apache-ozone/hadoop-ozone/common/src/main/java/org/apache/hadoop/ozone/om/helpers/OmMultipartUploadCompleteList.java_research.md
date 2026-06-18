# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartUploadCompleteList.java

Purpose: Holds the client-supplied part list for a complete multipart upload request.

Important APIs/types/functions: Constructor copies the supplied part-number to ETag map into a `LinkedHashMap`. `getMultipartMap` exposes it. `getPartsList` converts entries to protobuf `Part` messages, setting both `partName` and `eTag` to the ETag for backward compatibility.

Control flow and state: Iterates insertion order of the linked map when building the part list.

State and persistence behavior: Request helper only. The generated `Part` list is consumed by OM MPU completion logic to validate and combine persisted parts.

Dependencies and integration points: Used by complete MPU request paths and Ozone Manager protocol `Part`.

Risks: `getMultipartMap` exposes mutable internal map. No sorting is applied, so caller-provided order matters unless downstream sorts/validates. Null ETags can fail protobuf construction.

Test signals: Part-list conversion order, backward-compatible partName equals ETag, mutable map expectations, and completion validation for sorted/unsorted part maps.
