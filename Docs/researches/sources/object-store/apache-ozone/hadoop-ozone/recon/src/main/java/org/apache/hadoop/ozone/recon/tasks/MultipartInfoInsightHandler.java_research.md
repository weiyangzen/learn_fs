# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/MultipartInfoInsightHandler.java

Purpose: `OmTableHandler` for multipart upload info. It maintains counts and byte sizes for in-progress multipart uploads.

Important APIs: `handlePutEvent`, `handleDeleteEvent`, `handleUpdateEvent`, and `getTableSizeAndCount`.

Control flow and persistence: PUT increments object count by one and adds each part's data and replicated sizes. DELETE decrements count and subtracts each part with floor-at-zero guards. UPDATE leaves count unchanged, subtracts sizes from old parts, and adds sizes from new parts. Reprocess scans the configured multipart table and aggregates sizes from each `OmMultipartKeyInfo` part map.

Dependencies and integration: depends on `OmMultipartKeyInfo`, protobuf `PartKeyInfo`, `ReconBasicOmKeyInfo`, OM table access, and caller-provided stats maps from table insight tasks.

Risks: unchecked casts require event validator correctness. UPDATE subtraction does not floor at zero, unlike DELETE, so malformed old/new events can create negative counters. Warnings for negative sizes in DELETE are unreachable after floor-at-zero calculation because `newSize` cannot be negative. Part iteration assumes protobuf conversion succeeds for every part.

Test signals: `TestOmTableInsightTask` is the likely integration signal. Add direct tests for put/delete/update with multiple parts, missing old values, negative-counter prevention, and reprocess parity with incremental events.
