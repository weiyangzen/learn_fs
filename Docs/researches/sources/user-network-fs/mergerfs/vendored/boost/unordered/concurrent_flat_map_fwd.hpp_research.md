# sources/user-network-fs/mergerfs/vendored/boost/unordered/concurrent_flat_map_fwd.hpp

Purpose: Forward-declares `concurrent_flat_map` and associated free functions without including the full implementation.

Important APIs, types, and functions: Declares the class template with default `boost::hash`, `std::equal_to`, and `std::allocator<std::pair<Key const,T>>`; declares `operator==`, `operator!=`, `swap`, `erase_if`; defines `boost::unordered::pmr::concurrent_flat_map` when `<memory_resource>` is available; imports `boost::unordered::concurrent_flat_map` into namespace `boost`.

Control flow: Compile-time declarations only, with conditional PMR aliasing gated by `BOOST_NO_CXX17_HDR_MEMORY_RESOURCE`.

State and persistence behavior: No state; this header reduces include cost and breaks declaration cycles.

Dependencies and integration points: Includes Boost.Config, Boost.ContainerHash forward declarations, `<functional>`, `<memory>`, and optionally `<memory_resource>`.

Risks: The include-guard closing comment names `BOOST_UNORDERED_CONCURRENT_FLAT_MAP_HPP` instead of the actual forward header guard, a harmless maintenance typo. Consumers still need the full header for definitions.

Test signals: Compile tests should verify forward declaration usability in pointers/references and PMR alias availability under C++17 memory-resource support.
