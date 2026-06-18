# sources/test-tools/strace/tests/nlattr_cachereport-Xverbose.c

Purpose: compiles the cache-report nlattr test with verbose xlat output enabled by defining `XLAT_VERBOSE`.

Important APIs, types, and helpers: inherits `nlattr_cachereport.c` and its route-cache attribute tests, with `XLAT_VERBOSE` controlling value rendering.

Control flow: no local runtime logic; the base file’s `main` is compiled in verbose xlat mode.

State and persistence: no added state and no route table modification.

Dependencies and integration points: validates strace `-Xverbose` formatting for the same nlattr cases covered by the base file.

Risks and edge cases: verbose xlat strings can change when tables are renamed or constants are added.

Test signals: output should match the base cache-report cases with verbose xlat value presentation.
