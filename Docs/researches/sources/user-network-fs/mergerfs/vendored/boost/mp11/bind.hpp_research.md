# sources/user-network-fs/mergerfs/vendored/boost/mp11/bind.hpp

Purpose: Provides MP11 metafunction binding and placeholders.

Important APIs, types, and functions: `mp_bind_front`, `mp_bind_back`, `_1` through `_9`, `mp_arg<I>`, `mp_bind`, and `_q` variants.

Control flow: Bound arguments are evaluated at template instantiation time. Placeholders select call-site arguments; nested binds and front/back binds are recursively evaluated before applying the target metafunction.

State and persistence behavior: Compile-time only.

Dependencies and integration points: Depends on `algorithm.hpp`, `utility.hpp`, and `<cstddef>`. Used by Describe member filtering and user MP11 expressions.

Risks: Alias-template expansion limitations require `mp_defer`; incorrect placeholder index produces an out-of-range `mp_at_c` error. Nested bind complexity can increase diagnostics.

Test signals: Static assertions for front/back binding, placeholders, nested bind expressions, quote variants, and invalid placeholder arity diagnostics.
