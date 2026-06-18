# sources/user-network-fs/mergerfs/vendored/boost/config/detail/suffix.hpp

Purpose: final normalization layer for Boost.Config. After user, compiler, platform, and standard-library headers have contributed raw feature macros, this file derives implications, defines portable helper macros/types, checks standard headers, and adds compatibility aliases.

Important APIs/macros: defines defaults for `BOOST_SYMBOL_EXPORT/IMPORT/VISIBLE`, `BOOST_STD_EXTENSION_NAMESPACE`, `BOOST_STATIC_CONSTANT`, `BOOST_USE_FACET`, `BOOST_HAS_FACET`, `BOOST_NESTED_TEMPLATE`, `BOOST_UNREACHABLE_RETURN`, `BOOST_DEDUCED_TYPENAME`, `BOOST_CTOR_TYPENAME`, `BOOST_RESTRICT`, `BOOST_MAY_ALIAS`, `BOOST_FORCEINLINE`, `BOOST_NOINLINE`, `BOOST_NORETURN`, `BOOST_DEPRECATED`, `BOOST_LIKELY`, `BOOST_UNLIKELY`, `BOOST_OVERRIDE`, `BOOST_ALIGNMENT`, `BOOST_DEFAULTED_FUNCTION`, `BOOST_DELETED_FUNCTION`, `BOOST_FINAL`, `BOOST_NOEXCEPT`, `BOOST_CONSTEXPR`, `BOOST_CXX14_CONSTEXPR`, `BOOST_INLINE_VARIABLE`, `BOOST_IF_CONSTEXPR`, `BOOST_ATTRIBUTE_UNUSED`, `BOOST_ATTRIBUTE_NODISCARD`, `BOOST_NULLPTR`, and type aliases such as `boost::long_long_type`, `boost::int128_type`, and `boost::float128_type` when supported.

Control flow/dependencies: includes `<limits.h>`, sometimes `<cstddef>`, `<typeinfo>`, `boost/config/helper_macros.hpp`, `<version>`, and `detail/cxx_composite.hpp`. It first repairs implications among legacy feature macros, then validates thread APIs, then defines helper wrappers, then maps deprecated macro names, then probes C++17/20/23 headers with `__has_include` and feature-test macros.

State and persistence: compile-time-only macro state and a few compile-time typedefs in namespace `boost`. No runtime persistence.

Integration points: every Boost library that includes `boost/config.hpp` receives these helpers. It is also the enforcement point for deprecated minimum requirements such as no template partial specialization.

Risks and test signals: high risk because it globally affects all Boost headers. Test with Boost.Config's full matrix: thread on/off modes, deprecated aliases, C++ standard modes, `__has_include` availability, MSVC `_MSVC_LANG`, CUDA/device compilation, no-exception/no-RTTI modes, and standard header feature-test coverage.
