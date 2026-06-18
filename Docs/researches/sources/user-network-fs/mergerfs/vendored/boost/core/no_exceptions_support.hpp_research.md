# sources/user-network-fs/mergerfs/vendored/boost/core/no_exceptions_support.hpp

Purpose: Macros that let Boost code write try/catch cleanup blocks that compile away when exceptions are disabled.

Important APIs, types, and functions: `BOOST_TRY`, `BOOST_CATCH(x)`, `BOOST_RETHROW`, `BOOST_CATCH_END`, and legacy support for `BOOST_NO_EXCEPTIONS`.

Control flow: With exceptions, macros expand to `try`, `catch`, and `throw`. Without exceptions, catch blocks become unreachable/disabled constructs and rethrow is omitted or adapted.

State and persistence behavior: No state.

Dependencies and integration points: Used by Boost components that support `BOOST_NO_EXCEPTIONS` builds while sharing one source body.

Risks: Cleanup paths hidden behind catch macros do not execute in no-exception mode. Macro syntax must remain balanced.

Test signals: Compile the same source with and without exception support; verify cleanup behavior in exception-enabled mode and syntax in disabled mode.
