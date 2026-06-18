# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_defer.hpp

Purpose: Provides deferred/evaluable metafunction primitives used to avoid premature hard errors in MP11.

Important APIs, types, and functions: `mp_if_c`, `mp_if`, `mp_valid`, `mp_defer`, `mp_eval_or`, `mp_eval_if`, `mp_eval_if_c`, `mp_cond`, and related implementation helpers.

Control flow: Template selection delays instantiation of branches until selected or proven valid. `mp_valid` detects whether `F<T...>` is well-formed, with alternate implementation for Intel.

State and persistence behavior: Compile-time only.

Dependencies and integration points: Core building block for MP11 utility, bind, algorithms, and SFINAE-heavy Boost headers.

Risks: Incorrect deferral causes eager instantiation and noisy compile failures. Branch arity and selected fallback types must match expected alias contracts.

Test signals: Static assertions for valid/invalid expressions, branch laziness, default fallbacks, conditional chains, Intel workaround builds, and alias-template failure cases.
