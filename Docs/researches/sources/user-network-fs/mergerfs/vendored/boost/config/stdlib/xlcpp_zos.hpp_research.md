# sources/user-network-fs/mergerfs/vendored/boost/config/stdlib/xlcpp_zos.hpp

Purpose: configures Boost for the IBM z/OS XL C/C++ standard library V2R1.

Important APIs/macros: validates `__TARGET_LIB__ >= 0x42010000`, emits `BOOST_ASSERT_CONFIG` for newer unknown library versions, defines `BOOST_STDLIB`, `BOOST_HAS_MACRO_USE_FACET`, and a conservative set of missing C++11/14/17 standard library facilities including type_traits, initializer_list, addressof, smart pointers, allocator/pointer_traits, most C++11 headers, std::align, shared_mutex, exchange, invoke, apply, and iterator traits.

Control flow/dependencies: version gate followed by a fixed missing-feature profile.

State and persistence: compile-time standard-library state only.

Integration points: selected with z/OS compiler/platform configs. Locale facet handling flows through `BOOST_USE_FACET` in `suffix.hpp`.

Risks and test signals: risk is strict version support and broad feature disabling if z/OS library updates add facilities. Test `__TARGET_LIB__` values, locale facet macros, all marked standard headers, allocator/smart pointer support, and C++14/17 library features.
