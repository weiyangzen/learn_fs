# sources/storage-engines/tikv/components/engine_traits_tests/src/iterator.rs

Purpose: Provides shared conformance tests for engine and snapshot iterator semantics.

Important APIs and control flow: Generic helper functions test empty iterators, forward/reverse traversal, seek-then-forward, seek-then-reverse, changing direction, `seek_for_prev`, seek misses, and seek-for-prev misses. Each helper is run against both direct engine iterators and snapshot iterators over `CF_DEFAULT`. Invalid iterator states are expected to return false for validity and to error or panic on movement/key/value access.

State, persistence, and dependencies: Each test writes small ordered key sets into temporary engines. Snapshot iterator tests rely on snapshot-created consistent views.

Integration points, risks, and test signals: This is the main behavioral signal for iterator validity, ordering, direction changes, and miss positioning. Risks include backend differences in invalid movement behavior, key/value access panics, and seek semantics at boundaries.
