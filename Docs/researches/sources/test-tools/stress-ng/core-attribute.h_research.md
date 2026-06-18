# sources/test-tools/stress-ng/core-attribute.h

Purpose: compiler attribute portability layer.

Important APIs and control flow: maps feature/version probes to macros such as `WARN_UNUSED`, `NORETURN`, `WEAK`, `PACKED`, `ALWAYS_INLINE`, `NOINLINE`, `OPTIMIZE*`, `ALIGNED`, `SECTION`, `CONST`, `PURE`, `MLOCKED_TEXT`, `FORMAT`, and `RETURNS_NONNULL`.

State and persistence: compile-time only.

Dependencies and integration: included by most low-level headers to express compiler hints without hard-coding GCC/Clang behavior.

Risks and test signals: version macro mistakes can cause unsupported attributes or missed optimization/safety diagnostics. Signal is clean compilation across GCC, Clang, ICC, PCC, musl-gcc, and platform targets.
