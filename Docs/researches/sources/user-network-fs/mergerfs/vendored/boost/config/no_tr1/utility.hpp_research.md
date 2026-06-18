# sources/user-network-fs/mergerfs/vendored/boost/config/no_tr1/utility.hpp

Purpose: safely includes standard `<utility>` without recursively including Boost.TR1 utility wrappers.

Important APIs/macros: defines `BOOST_CONFIG_UTILITY`; temporarily sets `BOOST_TR1_NO_RECURSION` and `BOOST_CONFIG_NO_UTILITY_RECURSION`; includes `<utility>`; and restores macro state when the wrapper owns the temporary guard.

Control flow/dependencies: simple guard/setup/include/cleanup pattern. Depends only on `<utility>`.

State and persistence: temporary preprocessor state only.

Integration points: heavily used by standard-library selectors because `<utility>` is a small C++ standard header that exposes many vendor library macros.

Risks and test signals: risk is recursive inclusion or leaked recursion suppression. Test include path setups where Boost.TR1 appears before system headers and verify vendor macros remain visible.
