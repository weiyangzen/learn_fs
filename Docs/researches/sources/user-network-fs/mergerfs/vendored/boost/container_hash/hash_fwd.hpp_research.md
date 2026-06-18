# sources/user-network-fs/mergerfs/vendored/boost/container_hash/hash_fwd.hpp

Purpose: Forward-declaration header for Boost.ContainerHash so clients can declare APIs without pulling the full hashing implementation.

Important APIs, types, and functions: Declares range traits in `boost::container_hash`, `boost::hash<T>`, `hash_combine`, `hash_range`, `hash_unordered_range`, and `hash_is_avalanching`.

Control flow: None; compile-time declarations only.

State and persistence behavior: No state.

Dependencies and integration points: Includes `<cstddef>` for `std::size_t`. Used by detail headers to avoid cycles and by public headers as a lightweight contract.

Risks: Signature drift with `hash.hpp` would break dependent headers. Forward declarations constrain later definitions and overload visibility.

Test signals: Include-order tests that include `hash_fwd.hpp` before and after `hash.hpp`; compile declarations in translation units that only need pointers/references to hash types.
