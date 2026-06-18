# sources/user-network-fs/mergerfs/vendored/boost/config/helper_macros.hpp

Purpose: provides minimal C-compatible preprocessor helpers used by Boost.Config and other Boost headers.

Important APIs/macros: `BOOST_STRINGIZE(X)` expands macro arguments before stringizing through `BOOST_DO_STRINGIZE(X)`. `BOOST_JOIN(X, Y)` expands macro arguments before token pasting through `BOOST_DO_JOIN` and `BOOST_DO_JOIN2`.

Control flow/dependencies: no includes and no runtime code. The only flow is macro indirection to force the preprocessor expansion order required by the C/C++ macro rules.

State and persistence: none beyond preprocessor expansion.

Integration points: used by compiler-name strings, pragma message construction, generated identifiers, and config diagnostics.

Risks and test signals: low risk but central. Incorrect indirection would break version strings and token-paste based macros. Test with macro-valued arguments such as `BOOST_STRINGIZE(__LINE__)` and `BOOST_JOIN(foo_, BAR)` where `BAR` is itself a macro.
