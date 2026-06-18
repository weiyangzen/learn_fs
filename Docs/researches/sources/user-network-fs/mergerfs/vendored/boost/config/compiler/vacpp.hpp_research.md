# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/vacpp.hpp

Purpose: configures Boost for IBM VisualAge and older IBM XL C++ identified by `__IBMCPP__`.

Important APIs/macros: defines `BOOST_COMPILER`, version gates for unsupported compilers, `BOOST_MAY_ALIAS` for `__IBMCPP__ >= 1310`, and `_THREAD_SAFE`-based `BOOST_HAS_THREADS`. It disables older IBM defects including member template friends, in-class integral initialization, pointer-to-member template parameters, complete value initialization, and partial specialization default arguments. C++11 feature availability is driven by IBM-specific macros such as `__IBMCPP_AUTO_TYPEDEDUCTION`, `__IBMCPP_DECLTYPE`, `__IBMCPP_RVALUE_REFERENCES`, and `__IBMCPP_VARIADIC_TEMPLATES`; C++14/17 features are checked with SD-6 macros.

Control flow/dependencies: selected after z/OS XL and Linux clang-based XL checks, so it covers VisualAge and big-endian/legacy IBM XL configurations. It is a local macro table with no includes.

State and persistence: compile-time macros only.

Integration points: commonly pairs with `platform/aix.hpp` and `stdlib/vacpp.hpp`. `suffix.hpp` derives portable helpers such as `BOOST_DEFAULTED_FUNCTION`, `BOOST_MAY_ALIAS`, and thread validation from these macros.

Risks and test signals: risk is confusion between old `vacpp.hpp`, clang-based `xlcpp.hpp`, and z/OS `xlcpp_zos.hpp`. Test by preprocessing compiler selection and running Boost.Config probes for IBM-specific feature macros and thread flags.
