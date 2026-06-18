# sources/user-network-fs/mergerfs/vendored/boost/container_hash/detail/hash_integral.hpp

Purpose: implements `boost::hash_value` for integral types, including compiler-provided 128-bit integers not always recognized by standard type traits.

Important APIs/types/functions: in `boost::hash_detail`, defines wrappers `is_integral<T>`, `is_unsigned<T>`, and `make_unsigned<T>` over standard traits, with `__int128_t` and `__uint128_t` specializations when `__SIZEOF_INT128__` is defined. Defines primary template `hash_integral_impl<T, bigger_than_size_t, is_unsigned, size_t_bits, type_bits>` plus specializations for small values, signed larger-than-size_t values, unsigned 64-bit values on 32-bit `size_t`, unsigned 128-bit values on 32-bit `size_t`, and unsigned 128-bit values on 64-bit `size_t`. Public API is `template <typename T> enable_if<is_integral<T>::value, size_t>::type boost::hash_value(T v)`.

Control flow/dependencies: includes `hash_mix.hpp`, `<type_traits>`, `<cstddef>`, and `<climits>`. Small integral values cast directly to `size_t`. Large signed values convert through unsigned magnitude handling so negative values hash via bitwise complement. Large unsigned values split into 32- or 64-bit limbs and fold each limb with `hash_mix(seed)`.

State and persistence: stateless pure hashing; no persistent state.

Integration points: used by Boost.ContainerHash as the integral overload behind `boost::hash`. Depends on `hash_mix` avalanche quality for values wider than `size_t`.

Risks and test signals: risk is platform assumptions around `__int128_t` names, signed negative conversion, and unsupported `size_t` widths beyond 32/64. Tests should cover all standard integral types, bool/char variants, signed negatives, 64-bit integers on 32-bit targets, 128-bit integers on GCC/Clang, and SFINAE exclusion for non-integral types.
