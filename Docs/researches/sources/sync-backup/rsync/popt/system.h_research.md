# sources/sync-backup/rsync/popt/system.h

Purpose: Portability and utility include for the bundled popt code. It pulls in generated config, standard headers, allocation helper declarations/macros, `stpcpy()` fallback, secure `getenv()` mapping, and compiler attribute macros.

Important APIs, types, and functions: Defines `_isspaceptr()` for unsigned-char-safe whitespace checks. Declares or macro-defines `xmalloc()`, `xcalloc()`, `xrealloc()`, and `xstrdup()`. Supplies an inline `stpcpy()` when missing. Defines `UNUSED`, `FORMAT`, and `NORETURN`. Includes `popt.h` after preparing the environment.

Control flow: Mostly preprocessor logic. When `HAVE_MCHECK_H` and GCC are present, allocation macros call libc allocation and abort via `vmefail()` on failure, improving mtrace locations. Otherwise they map directly to libc allocation functions. `getenv()` may be remapped to `secure_getenv()` or `__secure_getenv()`.

State and persistence behavior: No runtime state beyond process-wide allocation and environment access behavior. The secure getenv remapping affects any popt source that includes this header.

Dependencies and integration points: Depends on `config.h`, libc headers, optional `mcheck.h`, and `popt.h`. Included by all bundled popt implementation files.

Risks and test signals: Risks include GNU statement-expression allocation macros reducing portability, `xstrdup()` assuming non-null strings, and build differences when secure getenv is unavailable. Tests are mainly compile-time/build-matrix checks plus config parsing under privileged/sanitized environment assumptions.
