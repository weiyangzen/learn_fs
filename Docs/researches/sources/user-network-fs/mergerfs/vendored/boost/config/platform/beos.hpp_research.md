# sources/user-network-fs/mergerfs/vendored/boost/config/platform/beos.hpp

Purpose: configures Boost platform macros for BeOS.

Important APIs/macros: defines `BOOST_PLATFORM "BeOS"`, disables `<cwchar>` and `<cwctype>` with `BOOST_NO_CWCHAR` and `BOOST_NO_CWCTYPE`, enables `BOOST_HAS_UNISTD_H`, `BOOST_HAS_BETHREADS`, and conditionally `BOOST_HAS_THREADS` unless `BOOST_DISABLE_THREADS` is set.

Control flow/dependencies: static macros plus `boost/config/detail/posix_features.hpp` for POSIX feature derivation.

State and persistence: compile-time macro state only.

Integration points: selected when `__BEOS__` is present. Thread normalization in `suffix.hpp` recognizes `BOOST_HAS_BETHREADS` as a valid threading API.

Risks and test signals: risk is thread support mismatch when BeOS headers or libraries differ. Test with Be threading primitives, POSIX header probes, and wide-character compile tests.
