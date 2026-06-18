# sources/user-network-fs/mergerfs/vendored/boost/describe/detail/cx_streq.hpp

Purpose: Provides constexpr string equality for descriptor names.

Important APIs, types, and functions: `boost::describe::detail::cx_streq(char const*, char const*)`.

Control flow: Recursively compares current characters and advances until mismatch or null terminator.

State and persistence behavior: No state.

Dependencies and integration points: Used by `members.hpp` to detect hidden inherited members by descriptor name.

Risks: Recursive constexpr depth depends on string length and compiler support; expects valid null-terminated strings.

Test signals: Static assertions for equal strings, unequal strings, prefix cases, empty strings, and descriptor-name hiding.
