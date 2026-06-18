# sources/user-network-fs/mergerfs/vendored/boost/limits.hpp

Purpose: Compatibility wrapper around `<limits>` plus fallback `std::numeric_limits` specializations for long long on old standard libraries.

Important APIs, types, and functions: Includes either `<limits>` or `<limits.h>` depending on Boost config; conditionally specializes `std::numeric_limits` for `boost::long_long_type` and `boost::ulong_long_type`.

Control flow: Preprocessor selects standard limits support or hand-written min/max/digits/signedness values using compiler macros.

State and persistence behavior: Compile-time traits only.

Dependencies and integration points: Used by `cstdint.hpp` and other Boost code needing numeric limits on legacy platforms.

Risks: Specializing in namespace `std` is only for missing implementation support and must match actual type widths. Incorrect LLONG/ULLONG macro detection breaks numeric traits.

Test signals: Static assertions for numeric_limits values and digits for signed/unsigned long long under legacy config macros.
