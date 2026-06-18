# sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/MockDataDistributor.h

Purpose: declares the mock data distributor entry point used by DD tests.

Important APIs and functions: `class MockDataDistributor` exposes `Future<Void> run(Reference<DDSharedContext> context, Reference<DDMockTxnProcessor> txnProcessor)`.

Control flow: implementation is elsewhere. The mock runner takes the same shared context shape as the real DD but uses `DDMockTxnProcessor`, allowing DD control-plane actors to operate against `MockGlobalState`.

State and persistence: no state in the header. Runtime state lives in `DDSharedContext` and the mock transaction processor's `MockGlobalState`; all persistence is in-memory.

Dependencies and integration: includes `DataDistribution.h`, `DDSharedContext.h`, and `MockGlobalState.h`. It bridges mock tests into the same component graph as production DD.

Risks: if DD code bypasses `IDDTxnProcessor` and uses real `Database` APIs, this mock entry point will fail or miss coverage. Header coupling to `DataDistribution.h` can increase rebuild cost.

Test signals: mock DD tests should verify `run()` can initialize team collection, tracker, queue, and move flows using `DDMockTxnProcessor`.
