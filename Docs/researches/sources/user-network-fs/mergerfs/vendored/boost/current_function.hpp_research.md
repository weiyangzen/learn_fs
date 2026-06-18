# sources/user-network-fs/mergerfs/vendored/boost/current_function.hpp

Purpose: Defines `BOOST_CURRENT_FUNCTION`, a portable macro for the current function signature/name.

Important APIs, types, and functions: Macro `BOOST_CURRENT_FUNCTION`; internal `boost::detail::current_function_helper()` scopes the preprocessor definitions.

Control flow: Preprocessor chooses `__PRETTY_FUNCTION__`, `__FUNCSIG__`, `__FUNCTION__`, `__FUNC__`, `__func__`, or `"(unknown)"` based on compiler and `BOOST_DISABLE_CURRENT_FUNCTION`.

State and persistence behavior: No state.

Dependencies and integration points: Used by assertions, diagnostics, exceptions, and logging helpers.

Risks: Macro expands to different string formats by compiler, affecting diagnostics and tests that compare exact messages.

Test signals: Compile on major compilers; verify macro is defined inside functions and respects `BOOST_DISABLE_CURRENT_FUNCTION`.
