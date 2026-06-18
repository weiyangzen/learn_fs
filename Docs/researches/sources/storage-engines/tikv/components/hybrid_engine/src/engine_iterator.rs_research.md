# sources/storage-engines/tikv/components/hybrid_engine/src/engine_iterator.rs

Purpose: iterator facade over either disk or region-cache snapshot iterators.

Important APIs/types/functions: `HybridEngineIterator`, disk/cache constructors, `Iterator` trait implementation, `HybridEngineIterMetricsCollector`, and `MetricsExt`.

Control flow: snapshot selection creates either a disk or cache iterator; all seek/navigation/key/value/valid and metric calls dispatch to the selected inner iterator.

State and persistence: iterator cursor state lives in the underlying engine iterator; wrapper has no persistence.

Dependencies/integration: used by `HybridEngineSnapshot::iterator_opt`; depends on `engine_traits` iterator/metrics traits.

Risks: metrics reflect only the selected engine, not an aggregate; cache-vs-disk routing is controlled outside this file.

Test signals: cache-backed iteration is exercised in snapshot tests.
