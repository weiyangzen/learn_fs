# sources/storage-engines/tikv/components/crossbeam-skiplist/src/lib.rs

Purpose: This crate root defines the public shape and documentation for TiKV's vendored `crossbeam-skiplist` component. It presents `SkipMap` and `SkipSet` as ordered concurrent alternatives to `BTreeMap` and `BTreeSet`, and documents lock-free operation, race semantics, immutable value access, epoch reclamation, and performance tradeoffs.

Important APIs and types: It conditionally exposes `base` and reexports `SkipList` when `alloc` and pointer atomics are available. With `std`, it exposes `map`, `set`, and reexports `SkipMap` and `SkipSet`. The crate uses `#![no_std]`, enables `alloc`/`std` conditionally, and warns on missing docs and unsafe operations in unsafe functions.

Control flow: There is no runtime control flow beyond conditional module compilation. The documentation examples demonstrate concurrent insertion/removal and ordered iteration.

State and persistence behavior: No state is stored in this file. It controls compile-time module availability.

Dependencies and integration points: It depends on `crossbeam-epoch` and `crossbeam-utils` through submodules. The private `seal` module references `crossbeam_skiplist_offical::SkipList<(), ()>` only to keep cargo machete from flagging the dependency as unused.

Risks: Feature gating is central: `base` is available in no-std alloc builds, while `SkipMap`/`SkipSet` require `std`. The documentation explicitly warns that individual operations are atomic but multi-call workflows can race logically.

Test signals: Doctests in this root document public examples, while dedicated tests under `tests/` validate behavior.
