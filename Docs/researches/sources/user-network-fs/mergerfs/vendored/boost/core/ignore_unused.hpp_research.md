# sources/user-network-fs/mergerfs/vendored/boost/core/ignore_unused.hpp

Purpose: Small utility to suppress unused variable warnings.

Important APIs, types, and functions: `boost::ignore_unused()` overloads for no arguments, one argument, and variadic arguments where supported.

Control flow: Runtime functions do nothing; they cast/use arguments only enough to satisfy compilers.

State and persistence behavior: No state.

Dependencies and integration points: Uses Boost config for variadic/rvalue support. Widely usable by headers that intentionally ignore parameters in portable code.

Risks: Must not evaluate arguments more than normal function-call evaluation; cannot suppress unused type/template warnings.

Test signals: Compile with high warning levels for ignored local variables and parameters across C++03/C++11 modes.
