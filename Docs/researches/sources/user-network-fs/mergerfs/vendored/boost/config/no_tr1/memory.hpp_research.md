# sources/user-network-fs/mergerfs/vendored/boost/config/no_tr1/memory.hpp

Purpose: safely includes standard `<memory>` while avoiding recursive Boost.TR1 memory wrappers.

Important APIs/macros: defines `BOOST_CONFIG_MEMORY`; temporarily sets `BOOST_TR1_NO_RECURSION` and `BOOST_CONFIG_NO_MEMORY_RECURSION`; includes `<memory>`; and unsets the temporary macros when this wrapper created them.

Control flow/dependencies: no logic beyond the standard `no_tr1` wrapper pattern. Depends on `<memory>`.

State and persistence: temporary preprocessor-only state.

Integration points: used during library detection or compatibility includes where Boost must inspect the vendor standard library directly.

Risks and test signals: macro lifetime bugs can affect later Boost.TR1 headers. Test repeated inclusion and caller-owned `BOOST_TR1_NO_RECURSION` preservation.
