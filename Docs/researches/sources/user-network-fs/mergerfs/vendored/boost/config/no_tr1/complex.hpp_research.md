# sources/user-network-fs/mergerfs/vendored/boost/config/no_tr1/complex.hpp

Purpose: includes the real standard `<complex>` while blocking recursive Boost.TR1 replacement headers.

Important APIs/macros: defines `BOOST_CONFIG_COMPLEX`; temporarily defines `BOOST_TR1_NO_RECURSION` and `BOOST_CONFIG_NO_COMPLEX_RECURSION` when needed; includes `<complex>`; then undoes the temporary definitions it owns.

Control flow/dependencies: same pattern as the other `no_tr1` wrappers. It depends on `<complex>` and the Boost.TR1 recursion guard macro.

State and persistence: temporary compile-time macro state only.

Integration points: used by configuration probes that need vendor standard-library macros from the real standard header, not Boost.TR1 forwarding headers.

Risks and test signals: risk is include-path recursion or macro leakage. Test with repeated includes and with `BOOST_TR1_NO_RECURSION` pre-defined by a caller.
