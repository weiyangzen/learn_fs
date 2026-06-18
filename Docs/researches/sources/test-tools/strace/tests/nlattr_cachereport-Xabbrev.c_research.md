# sources/test-tools/strace/tests/nlattr_cachereport-Xabbrev.c

Purpose: compiles the cache-report nlattr test with abbreviated xlat output enabled by defining `XLAT_ABBREV`.

Important APIs, types, and helpers: inherits `nlattr_cachereport.c`, including `RTM_NEWCACHEREPORT`, `CACHE_REPORT_*`, `TEST_NLATTR_*`, `XLAT_ABBREV`, and address-family xlat helpers.

Control flow: no local runtime logic. The included source runs the same cache-report attribute cases but prints xlat values in abbreviated mode.

State and persistence: no local state and no persistent route changes.

Dependencies and integration points: integrates with strace `-Xabbrev` expected-output variants for xlat formatting.

Risks and edge cases: any change in the base file or xlat mode formatting affects this wrapper.

Test signals: same structural output as `nlattr_cachereport.c`, with abbreviated symbolic xlat rendering.
