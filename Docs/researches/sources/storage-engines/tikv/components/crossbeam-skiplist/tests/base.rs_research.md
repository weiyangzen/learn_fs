# sources/storage-engines/tikv/components/crossbeam-skiplist/tests/base.rs

Purpose: This is the direct regression suite for the low-level guarded `base::SkipList` API. It validates behavior that public wrappers hide, especially guard usage, explicit `RefEntry` release, owned iteration, and destructor timing under epoch reclamation.

Important APIs and helpers: Tests use `SkipList`, `base::RefEntry`, `crossbeam_epoch::pin`, custom collectors, `Arc`, bounds, and a local `Entry` wrapper whose `Drop` calls `release_with_pin`. Test cases cover `new`, `is_empty`, `insert`, `remove`, `front`, `back`, entry navigation, `get`, `lower_bound`, `upper_bound`, `get_or_insert`, `get_or_insert_with`, `owned_iter`, `iter`, `range`, `into_iter`, `clear`, and drop behavior.

Control flow: Most tests build known integer maps, perform ordered mutations, and collect keys/values through entries or iterators. Panic and concurrency tests use `catch_unwind`, sleeping writer races, and spawned threads. The drop test uses a custom collector and explicit `flush` calls to observe deferred destruction.

State and persistence behavior: All state is in-memory. The suite tracks list length, removed-entry flags, explicit release behavior, and atomic counters for dropped keys and values.

Dependencies and integration points: It is the closest consumer of `base.rs`, so it catches lower-level API regressions before `SkipMap`/`SkipSet` wrappers are involved.

Risks: Some concurrency timing uses sleeps and therefore tests only selected interleavings. The direct API requires careful release discipline, and the local wrapper is part of the test safety model.

Test signals: Strong signals include sorted traversal after deletion, exact range outputs for inclusive/exclusive bounds, unchanged state after closure panic, closure execution despite discarded result, owned iterator validity across a spawned thread, clear-to-zero, and destructor counts after epoch flush.
