# sources/user-network-fs/mergerfs/vendored/boost/config/no_tr1/functional.hpp

Purpose: safely includes standard `<functional>` without routing through Boost.TR1 wrapper headers.

Important APIs/macros: defines `BOOST_CONFIG_FUNCTIONAL`; temporarily defines `BOOST_TR1_NO_RECURSION` and `BOOST_CONFIG_NO_FUNCTIONAL_RECURSION` only if the caller has not already requested no recursion.

Control flow/dependencies: include guard, temporary recursion macro setup, `<functional>` include, conditional cleanup.

State and persistence: temporary preprocessor state only; no runtime behavior.

Integration points: standard-library detection and compatibility headers can include this wrapper when they need real standard-library declarations/macros while Boost.TR1 include directories are active.

Risks and test signals: risk is accidental recursion through `boost/tr1/tr1/functional` or failing to preserve caller-owned `BOOST_TR1_NO_RECURSION`. Test with the macro pre-set and unset.
