# sources/user-network-fs/mergerfs/vendored/boost/config/pragma_message.hpp

Purpose: provides a portable `BOOST_PRAGMA_MESSAGE("message")` macro.

Important APIs/macros: if `BOOST_DISABLE_PRAGMA_MESSAGE` is set, the macro expands to nothing. Intel and MSVC use `__pragma(message(...))` with file and line context. GCC uses `_Pragma(BOOST_STRINGIZE(message(x)))`. Other compilers receive a no-op.

Control flow/dependencies: includes `boost/config/helper_macros.hpp` for `BOOST_STRINGIZE`, then compiler-specific macro branches.

State and persistence: no runtime state; affects compile diagnostics only.

Integration points: used by `header_deprecated.hpp`, `visualc.hpp`, and other config diagnostics that should not hard-code pragma syntax.

Risks and test signals: risk is malformed pragma syntax or too much diagnostic noise. Test with MSVC, GCC, Clang-as-GCC, Intel, disabled messages, and messages containing macro-expanded strings.
