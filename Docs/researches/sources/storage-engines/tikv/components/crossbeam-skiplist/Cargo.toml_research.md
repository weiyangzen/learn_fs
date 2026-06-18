# sources/storage-engines/tikv/components/crossbeam-skiplist/Cargo.toml

Purpose: manifest for TiKV’s vendored/forked `crossbeam-skiplist` component, a concurrent skip list used by the concurrency manager.

Important APIs and types: package metadata, features `std` and `alloc`, dependencies `crossbeam-epoch`, `crossbeam-utils`, and a renamed upstream dependency `crossbeam-skiplist-offical` for CI tracking. Test and example binary names are renamed to satisfy TiKV jemalloc checks.

Control flow: no runtime flow. Feature flags determine whether `std` and `alloc` APIs are available; disabling both is explicitly unsupported.

State and persistence: none directly; the library itself provides in-memory lock-free/concurrent data structures.

Dependencies and integration: `concurrency_manager` depends on this workspace crate for `SkipMap`. The upstream official dependency is present to keep critical bug-fix/security update visibility.

Risks: fork divergence from upstream is a maintenance risk, especially for memory reclamation and range iterator behavior. The dependency name contains a spelling typo (`offical`) that is harmless if consistently used but easy to misread.

Test signals: manifest points to base/map/set tests and simple example. Bench files in this subset compare performance against std maps and base skiplist.
