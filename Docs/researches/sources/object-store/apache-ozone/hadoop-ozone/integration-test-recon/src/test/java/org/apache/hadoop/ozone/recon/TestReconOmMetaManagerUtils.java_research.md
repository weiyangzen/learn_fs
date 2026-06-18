# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconOmMetaManagerUtils.java

## Purpose

This utility class provides wait helpers for Recon OM metadata processing in integration tests. It bridges asynchronous Recon event-buffer processing and delayed Recon container-key index updates.

## Important APIs, types, and functions

`waitForEventBufferEmpty(OMUpdateEventBuffer)` returns a `CompletableFuture<Void>` that waits for `eventBuffer.getQueueSize() == 0` and then sleeps briefly. `waitUntilReconKeyCounts(ReconContainerMetadataManager, Map<Long, Integer>)` repeatedly checks that each container has at least the expected key count. It uses `GenericTestUtils.waitFor()` and handles `IOException` from the metadata manager.

## Control flow, state, and persistence

The class stores no state. The event-buffer wait runs asynchronously and wraps failures in `RuntimeException`. The key-count wait polls for up to 90 seconds and treats transient read failures as not-ready rather than fatal, which is useful while Recon is concurrently applying RocksDB-backed updates.

## Dependencies and integration points

The helpers are used by tests that call `OzoneManagerServiceProviderImpl.syncDataFromOM()` and then need Recon task processing to complete before assertions. They integrate with `OMUpdateEventBuffer`, `ReconContainerMetadataManager`, and `GenericTestUtils`.

## Risks and test signals

An empty event buffer does not necessarily prove a dequeued batch has fully updated all derived indexes; the second helper addresses this by checking container-key counts directly. The extra sleep in `waitForEventBufferEmpty()` is a pragmatic stabilization delay. Positive signals are completed futures and converged per-container key counts.
