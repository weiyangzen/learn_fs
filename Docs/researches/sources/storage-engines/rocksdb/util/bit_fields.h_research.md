# sources/storage-engines/rocksdb/util/bit_fields.h

Purpose: defines a template system for tightly packing named fields into an unsigned underlying integer and updating those fields atomically. It is intended for concurrent state machines where a single lock-free atomic word is easier to reason about than multiple atomics or locks.

Important APIs and types: `BitFields<UnderlyingT,DerivedT>` stores `underlying`, exposes `Set`, `With`, `Get`, and `Ref` for field operations, and defines `kBitCount`. `NoPrevBitField` anchors field layout. `BoolBitField<Parent,Prev>` declares a one-bit bool field with get/set and OR/AND transforms. `UnsignedBitField<Parent,kBitCount,Prev>` declares an unsigned field with inferred value type, mask, get/set, clear, AND, OR, plus and minus transforms. `OrTransformer`, `AndTransformer`, and `AddTransformer` compose atomic fetch operations. `RelaxedBitFieldsAtomic` and `BitFieldsAtomic` wrap `std::atomic<U>` and provide load/store/CAS/exchange plus transform application with relaxed or acquire-release order.

Control flow and state: field operations are static template computations over bit offsets. Atomic `Apply` functions perform fetch-or, fetch-and, or fetch-add and optionally return before/after states. Debug builds track additive transform preconditions to catch inter-field overflow or underflow, except for top-bit fields where overflow can be intentionally ignored.

Dependencies and integration: depends on `<atomic>`, `<vector>`, `test_util/sync_point.h` for `testable_assert`, and `util/math.h` for `BitwiseAnd`. Integration search shows packed atomics in `cache/clock_cache.h`, including slot metadata and chain state.

Risks and test signals: layout correctness is compile-time but overlapping fields are permitted by design, so misuse can silently alias state. Additive transforms rely on unsigned overflow and debug-only preconditions; release builds will not catch bad underflow/overflow between fields. No direct test in this subset; confidence is mostly compile-time static assertions and downstream cache tests.
