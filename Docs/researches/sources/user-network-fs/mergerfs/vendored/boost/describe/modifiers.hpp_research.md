# sources/user-network-fs/mergerfs/vendored/boost/describe/modifiers.hpp

Purpose: Defines bitmask constants describing Boost.Describe member/base metadata.

Important APIs, types, and functions: Modifier constants such as `mod_public`, `mod_protected`, `mod_private`, `mod_virtual`, `mod_static`, `mod_function`, `mod_any_access`, `mod_inherited`, `mod_hidden`, and related masks.

Control flow: None; constants only.

State and persistence behavior: No state.

Dependencies and integration points: Used by `bases.hpp`, `members.hpp`, and consumers such as `hash.hpp` to filter descriptor lists.

Risks: Values are bitmask contract; changing them breaks descriptor filtering and external code using masks.

Test signals: Static assertions for mask combinations and filtering behavior in base/member describe APIs.
