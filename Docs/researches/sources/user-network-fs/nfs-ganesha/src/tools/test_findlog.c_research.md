# sources/user-network-fs/nfs-ganesha/src/tools/test_findlog.c

Purpose: `test_findlog.c` is intentionally not valid C; it is a fixture of logging-call patterns for `findlog.sh`. It exercises the script's ability to find log macro invocations while ignoring comments, strings, unrelated identifiers, and malformed contexts.

Important content: the file includes `LogTest()` calls with tabs, spaces, semicolons inside quoted strings, multi-argument calls, calls split over lines, macro-expanded calls, calls after assignments, `LogCrit()` in `else if` contexts, and lower-case `Logtest()` that should not match if matching is case-sensitive. Comments label cases where the expected extraction is currently too broad.

Control flow: there is no executable control flow. The apparent C statements are test input for a text parser. The fixture's ordering and line placement matter because expected results refer to concrete line numbers.

State and persistence: no runtime state. Persistence is the fixture text itself; changing whitespace or line numbers can affect `findlog.sh` expectations.

Dependencies and integration points: it integrates with `src/tools/findlog.sh` and whatever test harness compares discovered logging calls. It imitates Ganesha logging macros such as `LogWarn`, `LogCrit`, and arbitrary `LogTest`.

Risks: because the file is not valid C, build systems and static analyzers must not compile it. Test fragility is high: line number changes, macro formatting changes, or additional comments can change expected output. It also documents known overmatching areas rather than enforcing them.

Test signals: run `findlog.sh` against this fixture after parser changes; verify comments are ignored, multiple macro calls are discovered, quoted semicolons are handled, and non-log tokens such as `LogComponents` or `LogFile` are not mistaken for calls.
