# sources/sync-backup/bup/test/lib/wvpytest.py

Purpose: compatibility shim that maps historical bup WV test macros to pytest assertions.

Important APIs/types/functions: lower-case helpers `wvpass`, `wvfail`, `wvpasseq`, `wvpassne`, `wvpasslt`, `wvpassle`, `wvpassgt`, `wvpassge`, `wvexcept`, `wvcheck`, `wvmsg`, `wvstart`, and upper-case aliases `WVPASS`, `WVFAIL`, `WVPASSEQ`, `WVPASSNE`, `WVPASSLT`, `WVPASSLE`, `WVPASSGT`, `WVPASSGE`, `WVEXCEPT`, `WVCHECK`, `WVMSG`, `WVSTART`.

Control flow: each helper wraps a direct `assert`, pytest `raises`, or `print`. Equality and pass helpers optionally accept a failure value/message. Alias assignments at the bottom preserve legacy naming used throughout the test suite.

State and persistence behavior: no persistent state. `wvmsg`/`wvstart` print to stdout.

Dependencies/integration points: imported by most bup Python tests with `from wvpytest import *`, allowing older WV-style assertions to run under pytest without rewriting every test.

Risks and test signals: semantics are simpler than a dedicated assertion framework. `wvpass(cond=True)` defaults to passing if called without arguments, and `wvfail(cond=True)` defaults to failing unless passed a false condition, matching legacy macro usage.
