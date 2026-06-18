# sources/user-network-fs/mergerfs/vendored/boost/mp11/algorithm.hpp

Purpose: Large Boost.MP11 compile-time algorithm suite for type and value lists.

Important APIs, types, and functions: Includes transform/filter/fill/repeat/product/drop/iota/at/take/slice/back/pop/replace/remove/flatten/partition/sort/nth/find/reverse/fold/unique/all/none/any/replace_at/for_each/insert/erase/starts_with/rotate/power_set/partial_sum/iterate/pairwise/sliding/intersperse/split/join algorithms, plus `_q` quote variants.

Control flow: All algorithms are template metaprograms. Many use pack expansions, MP11 list primitives, `mp_fold`, `mp_append`, constexpr arrays for find/count, quicksort-like partitioning for sort/nth, and runtime `mp_for_each` that invokes a callable once per type object.

State and persistence behavior: Compile-time type/value transformations only; `mp_for_each` passes a runtime callable through repeated invocations but stores no global state.

Dependencies and integration points: Central dependency for Boost.Describe and ContainerHash described-class hashing. Depends on MP11 list/set/integral/utility/function and detail primitives.

Risks: Template instantiation depth and compiler workaround branches are key risks. Size mismatches in multi-list transform produce sentinel errors. Algorithms on empty lists can intentionally fail where no element exists.

Test signals: MP11 static assertion suite covering each algorithm, value-list support, large lists, MSVC/CUDA/GCC workaround configurations, and `mp_for_each` runtime invocation order.
