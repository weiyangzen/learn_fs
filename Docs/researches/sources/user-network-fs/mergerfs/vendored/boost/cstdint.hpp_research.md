# sources/user-network-fs/mergerfs/vendored/boost/cstdint.hpp

Purpose: Boost portable fixed-width integer typedef and integer literal macro header.

Important APIs, types, and functions: Defines/imports `boost::int8_t` through `uint_fast64_t`, `intmax_t`, `uintmax_t`, optional `intptr_t`/`uintptr_t` with `BOOST_HAS_INTPTR_T`, `BOOST_NO_INT64_T`, and C99-style `INT*_C`/`UINT*_C` macros when missing.

Control flow: Preprocessor chooses system `<stdint.h>`/`<inttypes.h>` when reliable, old platform-specific branches, or hand-written typedefs based on `<limits.h>` widths. A post-include macro section fills constant macros.

State and persistence behavior: Compile-time typedef/macro definitions only.

Dependencies and integration points: Used by Boost.Core bit utilities, hashing, and any vendored Boost code needing fixed-width integers.

Risks: Highly platform-sensitive; wrong width detection is a compile-time hard error or ABI mismatch. Literal macros differ for MS/Borland suffixes, long, and long long.

Test signals: Compile on representative Windows, Linux, BSD, macOS, and old-compiler configurations; static assert widths and signedness; compile integer literal macros at boundary values.
