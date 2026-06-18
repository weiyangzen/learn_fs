# sources/user-network-fs/mergerfs/vendored/boost/core/bit.hpp

Purpose: Portable Boost.Core backport of C++20 `<bit>` utilities.

Important APIs, types, and functions: `bit_cast`, `countl_zero`, `countl_one`, `countr_zero`, `countr_one`, `popcount`, `rotl`, `rotr`, `has_single_bit`, `bit_width`, `bit_floor`, `bit_ceil`, `endian`/`endian_type`, and `byteswap`.

Control flow: Compile-time configuration selects compiler builtins and intrinsics for GCC/Clang/MSVC, with constexpr arithmetic fallbacks. Public functions assert integer/unsigned constraints where required, dispatch by integer width, and handle zero cases explicitly.

State and persistence behavior: Stateless arithmetic utilities.

Dependencies and integration points: Depends on Boost static assert/config/cstdint, `<limits>`, `<cstring>`, and `<cstdlib>`. Used by hashing, serialization, endian-sensitive code, and general Boost utilities.

Risks: Undefined behavior risks are avoided by width checks and `memcpy`/builtin bit_cast, but shift/rotation and `bit_ceil` overflow boundaries need care. Endian detection is platform macro dependent.

Test signals: Static and runtime tests for all unsigned widths; zero/all-ones values; rotation counts larger than bit width and negative counts; endian enum on supported platforms; byteswap known constants; constexpr compilation.
