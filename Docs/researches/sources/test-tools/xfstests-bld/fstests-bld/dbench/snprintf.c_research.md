<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/snprintf.c -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/snprintf.c

Source read: complete file, 981 lines, 22744 bytes, sha256 `a21ecbc52d8fe6626e13579b09b2d07c68ccb21ca75404fbd6a0810c8167f0c1`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/dbench/snprintf.c_research.md`.

Purpose: portability implementation of C99-like `snprintf`, `vsnprintf`, `asprintf`, and `vasprintf` for systems missing those functions or having non-C99 behavior. It is a bundled fallback derived from Patrick Powell/Mutt/Samba code.

Important APIs/types/functions: compile-time gates `HAVE_SNPRINTF`, `HAVE_VSNPRINTF`, `HAVE_C99_SNPRINTF`, `HAVE_C99_VSNPRINTF`, `HAVE_ASPRINTF`, and `HAVE_VASPRINTF` decide which replacements are emitted. Internal formatter functions include `dopr()` state-machine parser, `fmtstr()`, `fmtint()`, `fmtfp()`, `dopr_outch()`, and helpers for long double/long long support and decimal splitting.

Control flow: if the platform already has conforming `snprintf` and `vsnprintf`, the file emits only `dummy_snprintf()`. Otherwise `dopr()` scans the format string through states for flags, minimum width, precision, length modifier, and conversion, dispatching to string/integer/floating formatters and counting would-have-written length. Replacement `vsnprintf()` calls `dopr()`; replacement `snprintf()` wraps `vsnprintf()`; `vasprintf()` first computes length with `vsnprintf(NULL, 0, ...)`, allocates, and formats; `asprintf()` wraps `vasprintf()`.

State and persistence behavior: no persistent state. It writes only to caller-provided buffers or malloc-allocated strings. The `TEST_SNPRINTF` block provides a standalone diagnostic program comparing behavior with system `sprintf()`.

Dependencies and integration: uses `config.h`, standard varargs/string/ctype/stdlib headers, optional long double/long long support, and optional math only for the test harness. Integrated implicitly by linking into dbench builds on older platforms.

Risks: the formatter is old and only approximates full modern printf behavior; exponential/significant formats are parsed but routed through fixed-point formatting; `%n` is implemented; pointer formatting casts to `long`, which is width-sensitive; `vasprintf()` does not `va_end()` copied lists; floating conversion caps precision and uses custom arithmetic. Replacement of standard symbols can conflict with libc/linker behavior on partially conforming systems.

Test signals: compile with `-DTEST_SNPRINTF` and run the built-in comparisons. Build configuration should also include autoconf checks for C99 return-length semantics and targeted tests for truncation, `NULL` buffers with count zero, integer widths, and `asprintf()` allocation failure handling.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/snprintf.c -->
