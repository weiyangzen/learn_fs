<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/Makefile.am -->
# sources/security-integrity/audit-userspace/auparse/test/Makefile.am

## Purpose
Defines Automake build, distribution, and test targets for auparse's C, shell, Python, static-link, diff, and memory tests.

## Important APIs, types, and functions
Declares `noinst_PROGRAMS`, `TESTS`, distributed scripts/reference logs, compiler/linker flags including ASAN and static variants, program sources/LDADD dependencies, and convenience targets `diffcheck`, `memcheck`, `pycheck`, `pydiffcheck`, and `pymemcheck`.

## Control flow
Normal `make check` runs shell and binary tests. Static builds add data buffer, LRU, and UID/name wrapper tests. Diff targets compare generated output with references; Python targets set `PYTHONPATH`, `LD_LIBRARY_PATH`, and `srcdir`; cleanup removes generated outputs and copied logs for out-of-tree builds.

## State and persistence behavior
Build artifacts, generated scripts, `.cur` comparison files, raw transformed logs, and copied test logs are transient and removed by clean rules.

## Dependencies and integration points
Links tests against `libauparse`, `libaudit`, and `libaucommon`. Integrates optional ASAN/static/Python3 build configuration and uses `auditd_raw.sed` for raw output normalization.

## Risks and test signals
Risks are stale references, missing static-only tests when dynamic builds are used, environment-sensitive Python paths, and brittle sed normalization. Test signals are `make check`, `diffcheck`, valgrind targets, Python diff output, and explicit `lru_cache_test`/`uid_name_wrap_test` under static builds.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/Makefile.am -->
