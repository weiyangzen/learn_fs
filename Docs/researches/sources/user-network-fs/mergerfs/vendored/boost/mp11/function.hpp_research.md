<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/function.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/function.hpp

## Purpose

Defines MP11 boolean and comparison metafunctions over integral-constant-like types. It supplies logical composition, sameness/similarity checks, signed-safe less-than comparison, and min/max helpers.

## Important APIs, Types, and Functions

Exports `mp_and`, `mp_all`, `mp_or`, `mp_any`, `mp_same`, `mp_similar`, `mp_less`, `mp_min`, and `mp_max`. Implementations use `mp_void`, `mp_count`, `mp_count_if`, `mp_min_element`, `mp_plus`, and lazy `mp_eval_if` utilities. Detected alias templates include `mp_and`, `mp_and`, `mp_all`, `mp_all`, `mp_or`, `mp_any`, `mp_any`, `mp_same`, `mp_similar`, `mp_less`, `mp_min`, `mp_max`. Implementation structs include `mp_and_impl`, `mp_or_impl`, `mp_same_impl`, `mp_similar_impl`.

## Control Flow

`mp_and` and `mp_or` short-circuit through lazy evaluation where needed; `mp_all`/`mp_any` compute aggregate truth over packs. `mp_same` counts exact type matches, `mp_similar` checks matching outer templates, and `mp_less` avoids signed/unsigned warning-prone direct comparisons. `mp_min`/`mp_max` delegate to min/max-element over an `mp_list`.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/integral.hpp`, `boost/mp11/utility.hpp`, `boost/mp11/detail/mp_list.hpp`, `boost/mp11/detail/mp_count.hpp`, `boost/mp11/detail/mp_plus.hpp`, `boost/mp11/detail/mp_min_element.hpp`, `boost/mp11/detail/mp_void.hpp`, `boost/mp11/detail/config.hpp`, `type_traits`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

Inputs are expected to expose `::value` convertible to bool or comparable numeric values. The file carries compiler workarounds for MSVC and GCC bugs; replacing them with simpler pack expressions can regress old supported compilers.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/function.hpp -->
