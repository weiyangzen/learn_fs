# sources/user-network-fs/mergerfs/vendored/boost/describe/detail/void_t.hpp

Purpose: Local `void_t` implementation for Boost.Describe SFINAE probes.

Important APIs, types, and functions: `make_void<T...>` and alias `void_t<T...>`.

Control flow: Compile-time alias substitution only.

State and persistence behavior: No state.

Dependencies and integration points: Included by Describe base/member detection headers.

Risks: Available only when `BOOST_DESCRIBE_CXX11` is defined; dependent headers must guard usage accordingly.

Test signals: Static SFINAE probes for valid/invalid descriptor expressions in C++11+ mode.
