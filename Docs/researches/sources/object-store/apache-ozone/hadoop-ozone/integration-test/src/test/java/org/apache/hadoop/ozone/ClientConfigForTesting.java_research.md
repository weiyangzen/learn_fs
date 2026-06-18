# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/ClientConfigForTesting.java

Purpose: fluent test helper that applies coherent Ozone client stream, chunk, block, and data-stream buffer sizes to a mutable configuration.

Important APIs/types/functions: `newBuilder(StorageUnit)`, setters for chunk size, block size, stream buffer size, stream buffer flush/max sizes, data stream flush/window/min packet sizes, `applyTo`, and `toBytes`. It writes to `OzoneClientConfig`, `OZONE_SCM_CHUNK_SIZE_KEY`, and `OZONE_SCM_BLOCK_SIZE`.

Control flow: callers choose an input `StorageUnit`, chain optional setters, then call `applyTo`. Missing values are defaulted from the chunk size: stream buffer size and flush size default to chunk size, stream max to twice flush, data-stream flush to four chunks, data min packet to quarter chunk, data window to eight chunks, and block size to twice stream max. The helper then mutates the typed `OzoneClientConfig`, writes it back with `setFromObject`, and stores chunk/block sizes as bytes.

State and persistence: no persistence beyond configuration mutation. The builder object is stateful: `applyTo` fills null fields, so subsequent setter calls after `applyTo` operate on already-defaulted values.

Dependencies and integration points: HDDS configuration object mapping, `StorageUnit` conversion, Ozone client stream tuning, SCM chunk size, and Ozone block size. It is intended for tests needing small deterministic block/chunk boundaries.

Risks: conversion uses `Math.round(unit.toBytes(value))`, and integer fields cast to `int`; oversized units/values can overflow for int-backed settings. Defaulting mutates the builder, so reuse across tests may leak choices. No validation enforces block size relative to stream max if caller sets inconsistent values manually.

Test signals: no tests in this file; downstream tests can infer behavior by checking generated key/block/chunk splitting under controlled config sizes.
