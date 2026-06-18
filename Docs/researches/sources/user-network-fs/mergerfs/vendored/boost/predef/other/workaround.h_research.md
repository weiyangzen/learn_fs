# sources/user-network-fs/mergerfs/vendored/boost/predef/other/workaround.h

Purpose: Provides version-comparison macros for conditional compiler/platform workarounds.

Important APIs, types, and functions: Defines `BOOST_PREDEF_WORKAROUND(symbol, comp, major, minor, patch)` and `BOOST_PREDEF_TESTED_AT(symbol, major, minor, patch)`.

Control flow: Under `BOOST_STRICT_CONFIG`, both macros expand to false-like `0`, disabling workaround branches. Otherwise `BOOST_PREDEF_WORKAROUND` checks that a detector symbol is nonzero and compares it to `BOOST_VERSION_NUMBER(major, minor, patch)`. `BOOST_PREDEF_TESTED_AT` normally returns whether the symbol is available; when `BOOST_DETECT_OUTDATED_WORKAROUNDS` is set, it allows versions up to the tested value and intentionally triggers a compile-time error for newer matching symbols.

State and persistence behavior: Pure preprocessor logic; no runtime state.

Dependencies and integration points: Uses `boost/predef/version_number.h` unless strict config disables comparisons. It mirrors Boost.Config-style workaround gates while using Boost.Predef version symbols.

Risks: The intentional `(1%0)` diagnostic for outdated workarounds is disruptive by design. Macro arguments must be detector numeric values, not arbitrary version strings.

Test signals: No direct `BOOST_PREDEF_DECLARE_TEST`; behavior is validated by compile-time use in consumers.
