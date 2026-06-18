<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/utility.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/utility.hpp

## Purpose

Provides MP11 utility metafunctions for identity, inheritance aggregation, lazy conditional evaluation, validity probing, quoted metafunctions, negation, and composition.

## Important APIs, Types, and Functions

Exports `mp_identity`, `mp_identity_t`, `mp_inherit`, `mp_eval_if_c`, `mp_eval_if`, `mp_eval_if_q`, `mp_eval_if_not`, `mp_eval_or`, `mp_valid_and_true`, `mp_cond`, `mp_quote`, `mp_quote_trait`, `mp_invoke_q`, `mp_not_fn`, `mp_not_fn_q`, `mp_compose`, and `mp_compose_q`. Detected alias templates include `mp_identity_t`, `mp_eval_if_c`, `mp_eval_if`, `mp_eval_if_q`, `mp_eval_if_not`, `mp_eval_if_not_q`, `mp_eval_or`, `mp_eval_or_q`, `mp_valid_and_true`, `mp_valid_and_true_q`, `mp_cond`, `mp_cond_`, `mp_invoke_q`, `mp_invoke_q`, `mp_invoke_q`, `mp_not_fn_q`, `mp_compose_helper`. Implementation structs include `mp_identity`, `mp_inherit`, `mp_eval_if_c_impl`, `mp_cond_impl`, `mp_quote`, `mp_quote_trait`, `mp_invoke_q_impl`, `mp_not_fn`, `mp_compose`, `mp_compose_q`.

## Control Flow

Lazy helpers select either an already-formed type or a deferred metafunction instantiation, preventing invalid branches from being instantiated. Quote helpers adapt templates and traits into uniform `Q::template fn` objects. Composition folds intermediate results through lists and applies quoted functions from right to left.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/integral.hpp`, `boost/mp11/detail/mp_list.hpp`, `boost/mp11/detail/mp_fold.hpp`, `boost/mp11/detail/mp_front.hpp`, `boost/mp11/detail/mp_rename.hpp`, `boost/mp11/detail/mp_defer.hpp`, `boost/mp11/detail/config.hpp`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

The utilities are SFINAE-sensitive; moving eager instantiations into lazy paths or vice versa changes compile-time failure behavior. Composition and conditional helpers rely on list/application primitives, so invalid quoted functions surface as template diagnostics.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/utility.hpp -->
