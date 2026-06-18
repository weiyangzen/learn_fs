# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/core.hpp

Purpose: Provides the common fast open-addressing implementation shared by Boost.Unordered flat and concurrent containers.

Important APIs, types, and functions: Major internals include `group15`, `pow2_size_policy`, `pow2_quadratic_prober`, hash mixing policies, `table_arrays`, stats structs/macros, allocator-construction traits, `table_locator`, `alloc_cted_insert_type`, `alloc_cted_or_fwded_key_type`, and `table_core`. `table_core` manages allocation, construction/destruction, lookup, insertion, erase, clear, swap, rehash, reserve, equality, stats, and element traversal.

Control flow: Metadata is organized in groups of 15 slots plus an overflow byte. `group15::match` uses SSE2, little-endian NEON, or portable bit operations to find candidate reduced-hash slots. Lookup probes groups quadratically and stops at non-overflowed groups. Insertions find an available slot, construct the element, set metadata, and update size; full tables allocate larger arrays and transfer elements with move-if-noexcept semantics. Erase destroys the element and recovers the slot, reducing max load when the erased slot may have caused overflow to limit probe drift.

State and persistence behavior: Stores hash, predicate, allocator via empty-base optimization; arrays of groups/elements; size/max-load control; and optional cumulative stats. It does not persist externally but supplies traversal and serialization support to higher layers.

Dependencies and integration points: Depends on Boost.Config, Boost.Predef, container hash traits, allocator/pointer traits, FOA stats, unordered diagnostics, and low-level bit/narrow/mulx helpers. `concurrent_table` specializes it with atomic metadata and atomic size control.

Risks: This is performance-critical unsafe-adjacent code: SIMD assumptions, metadata sentinel layout, fancy pointer support, exception-safety during transfer, and allocator construct behavior are all sensitive. Hash/predicate must be nothrow swappable for swap. Poor hash quality increases probing despite mixing policy support.

Test signals: Tests should cover SIMD and portable paths, heterogeneous lookup, allocator/fancy-pointer behavior, nontrivial move/copy exception paths, erase/insert drift, rehash/reserve invariants, equality, stats, sanitizer builds, and multiple architectures/endian configurations.
