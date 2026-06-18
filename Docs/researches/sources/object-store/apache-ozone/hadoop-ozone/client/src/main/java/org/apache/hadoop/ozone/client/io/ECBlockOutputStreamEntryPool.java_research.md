# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockOutputStreamEntryPool.java

Purpose: This class specializes `BlockOutputStreamEntryPool` for erasure-coded writes by creating `ECBlockOutputStreamEntry` instances instead of replicated `BlockOutputStreamEntry` instances.

Important APIs and types: It overrides `createStreamEntry` and narrows `getCurrentStreamEntry` to `ECBlockOutputStreamEntry`. Its builder input is `ECKeyOutputStream.Builder`, and it maps `OmKeyLocationInfo` fields into `ECBlockOutputStreamEntry.Builder`.

Control flow: All allocation, commit, hsync, metadata, exclude-list, and cleanup behavior remains inherited. Only entry instantiation changes: block ID, key, xceiver manager, pipeline, config, length, buffer pool, token, metrics, stream buffer arguments, and executor supplier are copied into the EC builder.

State and persistence behavior: State is inherited from the base pool. Persistent effects are still OM block allocation and key commit, but underlying entries write EC block groups rather than single replicated blocks.

Dependencies and integration points: This is the adapter between `ECKeyOutputStream` and the generic block pool. It also relies on base-class accessors for protected construction context.

Risks: The override does not propagate the `forRetry` flag into the EC entry builder, unlike the replicated pool; this is acceptable only if EC retry behavior is entirely stripe-level. The narrowed cast in `getCurrentStreamEntry` assumes the pool never contains replicated entries.

Test signals: Tests should verify EC builders create EC entries with the expected pipeline/config/token state, inherited preallocation and allocation work for EC locations, and `getCurrentStreamEntry` returns null or an EC entry safely.
