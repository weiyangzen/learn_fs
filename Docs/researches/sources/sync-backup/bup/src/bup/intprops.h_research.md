## sources/sync-backup/bup/src/bup/intprops.h

Purpose: vendored gnulib integer-properties header used for portable integer bounds and overflow-safe arithmetic in C code.

Important APIs: defines type/expression property macros (`TYPE_WIDTH`, `TYPE_MINIMUM`, `TYPE_MAXIMUM`, `EXPR_SIGNED`), overflow predicates (`INT_ADD_OVERFLOW`, `INT_SUBTRACT_OVERFLOW`, `INT_MULTIPLY_OVERFLOW`, division/remainder/shift variants), wrap helpers (`INT_*_WRAPV`), and success helpers (`INT_ADD_OK`, `INT_SUBTRACT_OK`, `INT_MULTIPLY_OK`). It uses compiler builtins when reliable and falls back to range calculations.

State and dependencies: preprocessor-only, dependent on `<limits.h>` and compiler feature detection. Bup uses it in the launcher for path-buffer growth and in `pyutil` allocation/type conversion helpers.

Risks and tests: macro arguments may be evaluated multiple times, so callers must avoid side effects. The header assumes two’s-complement integer representation without padding. Compiler-specific branches are high-risk for portability, but this is mature gnulib code. Bup test coverage is indirect via C extension builds, launcher execution, and memory allocation overflow paths where present.
