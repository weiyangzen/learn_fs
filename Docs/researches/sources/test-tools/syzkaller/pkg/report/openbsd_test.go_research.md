# Research: sources/test-tools/syzkaller/pkg/report/openbsd_test.go

Purpose: verifies OpenBSD-specific symbolization regexps used by the shared BSD reporter.

Important APIs/types/functions: `TestOpenbsdSymbolizeLine` defines `symbolizeLineTest` cases and delegates to `testSymbolizeLine` with `ctorOpenbsd`. It covers normal stack frames, inline frame expansion, missing symbols, and witness frame numbering.

Control flow: test data exercises matching of `at func+offset` and `#N func+offset` lines, then validates inserted file:line and inline markers from the fake symbolizer.

State and persistence: no filesystem writes and no persistent state.

Dependencies and integration points: uses common BSD symbolization test helpers and the OpenBSD constructor. It guards that OpenBSD remains compatible with `bsd.symbolizeLine`.

Risks: it does not cover OpenBSD title extraction, suppressions, or carriage-return offset behavior, so those require parse fixtures.

Test signals: failures mean OpenBSD stack/witness symbolization output changed or broke.
