# sources/test-tools/strace/tests/nlattr_cachereport-Xraw.c

Purpose: compiles the cache-report nlattr test with raw xlat output enabled by defining `XLAT_RAW`.

Important APIs, types, and helpers: inherits `nlattr_cachereport.c` and changes only xlat rendering mode through `XLAT_RAW`.

Control flow: no independent control flow; the included base executes all cache-report nlattr cases.

State and persistence: no local persistent state.

Dependencies and integration points: used by the strace `-Xraw` output mode tests for xlat values in route cache-report attributes.

Risks and edge cases: raw numeric formatting must stay aligned with the base test’s expected values.

Test signals: base cache-report traces should show raw numeric xlat output instead of symbolic-only forms.
