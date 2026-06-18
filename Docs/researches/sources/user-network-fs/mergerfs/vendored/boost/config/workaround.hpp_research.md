# sources/user-network-fs/mergerfs/vendored/boost/config/workaround.hpp

Purpose: provides Boost's version-aware workaround macros for compiler/library defects.

Important APIs/macros: defines `BOOST_WORKAROUND(symbol, test)` and `BOOST_TESTED_AT(value)`. In non-`BOOST_STRICT_CONFIG` mode it includes `boost/config.hpp`, defines many `*_WORKAROUND_GUARD` macros so undefined version symbols are safe to test, and implements the workaround expression using arithmetic that evaluates to true only when the symbol exists and satisfies the test. With `BOOST_DETECT_OUTDATED_WORKAROUNDS`, `BOOST_TESTED_AT` can intentionally cause diagnostics/errors when a compiler version exceeds the last tested version. In strict mode `BOOST_WORKAROUND` always expands to `0`.

Control flow/dependencies: guard macro definitions for many compiler and library version symbols, then macro implementation. No runtime code.

State and persistence: compile-time macro logic only.

Integration points: used throughout Boost to gate small compiler/library-specific code paths while documenting the last tested version.

Risks and test signals: risk is brittle preprocessor arithmetic and missing guard symbols for new config macros. Test undefined symbol cases, normal comparisons, `BOOST_TESTED_AT`, strict config, outdated workaround detection, and compilers with unusual preprocessor behavior.
