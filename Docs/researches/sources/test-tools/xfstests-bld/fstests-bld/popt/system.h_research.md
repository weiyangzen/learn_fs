# sources/test-tools/xfstests-bld/fstests-bld/popt/system.h

Purpose: portability and common include header for popt sources. It centralizes config includes, libc headers, whitespace macro, allocation wrappers, `stpcpy` fallback, secure getenv mapping, unused attribute, and inclusion of `popt.h`.

Important APIs/macros: `_isspaceptr`, `xmalloc`, `xcalloc`, `xrealloc`, `xstrdup`, fallback `stpcpy`, optional mcheck-backed allocation macros, secure `getenv` remap to `__secure_getenv`, and `UNUSED`.

Control flow/state: no runtime control flow beyond inline `stpcpy` and macro-expanded allocation calls. Allocation wrappers either call libc directly or exit on failure when mcheck/GCC macros are enabled.

Dependencies/integration: consumed by all popt C files and tests. Pulls in `config.h` when available, standard headers, optional `unistd.h`, and public `popt.h`.

Risks: macro replacement of allocation functions changes failure semantics across build configurations. `xstrdup` maps to `strdup` and can return NULL unless the mcheck macro branch is used. The secure getenv remap changes environment behavior for setuid-like contexts.

Test signals: portability builds across platforms and memory-check builds are the relevant coverage; normal parser tests exercise the macros indirectly.
