# sources/storage-engines/sqlite/src/msvc.h

Purpose: centralizes small Microsoft Visual C/C++ compatibility settings used by the SQLite source tree. It is a configuration header, not a runtime module.

Important macros: when `_MSC_VER` is defined, the file disables MSVC warnings that SQLite deliberately triggers or accepts, including function-pointer/data-pointer casts, unused parameters, constant conditionals, signed/unsigned conversions, unreachable code, and assignment in conditionals. For 32-bit MSVC it defines `SQLITE_4_BYTE_ALIGNED_MALLOC` after undefining any existing value. For MSVC versions older than 1800, it defines `HAVE_LOG2 0` when not already supplied.

Control flow: all behavior is preprocessor-only. Include guards prevent repeated application. The warning pragmas are active only under MSVC, the malloc alignment setting only under `_MSC_VER && !defined(_WIN64)`, and the `log2()` capability override only for older MSVC.

State and persistence: no state is allocated and no persistence is involved. Its effects are compile-unit configuration and compiler diagnostic behavior.

Dependencies and integration points: included by SQLite's internal configuration path for MSVC builds. `SQLITE_4_BYTE_ALIGNED_MALLOC` affects memory-alignment assumptions elsewhere in SQLite, especially on 32-bit Windows. `HAVE_LOG2` feeds feature-detection branches that decide whether SQLite may call `log2()` directly.

Risks: changing warning suppression can surface noisy build output or hide newly meaningful diagnostics. Incorrect `SQLITE_4_BYTE_ALIGNED_MALLOC` detection can affect code that assumes allocation alignment. The `HAVE_LOG2` fallback must not override a build system that explicitly defines it.

Test signals: compile amalgamation and non-amalgamation builds with 32-bit and 64-bit MSVC; verify no duplicate macro-definition warnings; confirm old MSVC builds avoid missing `log2()` references; and run memory-alignment-sensitive tests on 32-bit Windows.
