# sources/test-tools/stress-ng/core-pragma.h

Purpose: centralizes compiler pragma wrappers for optimization, warning suppression, and loop unrolling.

Important APIs/types: `STRESS_PRAGMA`, prefetch/noprefetch macros, optional no-hard-DFP target macro, diagnostic push/pop/warn-off macros, `STRESS_PRAGMA_WARN_CPP_OFF`, `PRAGMA_UNROLL_N`, and `PRAGMA_UNROLL`.

Control flow: compile-time branches select pragma spellings by compiler family/version and feature macros. Unsupported compilers receive empty macros.

State/persistence: no runtime state.

Dependencies/integration: consumed across code needing diagnostic suppression or optimization hints. Relies on config macros such as `HAVE_PRAGMA`, compiler family macros, and version predicates.

Risks: incorrect compiler detection can emit unsupported pragmas or fail to suppress warnings; empty fallback means performance hints disappear; warning-off macros can hide real diagnostics.

Test signals: GCC, Clang, ICC, and musl-style builds; warning-clean wrapped sections; and loop-unroll pragma smoke builds.
