<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/errs/msgtest.sh -->
# sources/test-tools/lcov/tests/genhtml/errs/msgtest.sh

- Purpose: Large genhtml/lcov diagnostic regression harness covering option validation, config includes, callbacks, cache errors, case-insensitive substitutions, deprecated RC options, MC/DC diagnostics, and message-count expectations.
- Important APIs/types/functions: Procedural shell script using `LCOV_BASE`, `DIFFCOV_OPTS`, version/annotate/select/criteria callback paths, compiler gates, and common.tst variables; no reusable shell functions.
- Control flow: Cleans artifacts, builds/captures baseline data, then runs many independent positive and negative `lcov`, `geninfo`, and `genhtml` checks, validating each with exit codes and greps.
- State and persistence behavior: Creates transient `.info`, `.log`, `.rc`, `.json`, cache directories, callback output directories, and report trees; its initial cleanup block defines the persistence boundary.
- Dependencies and integration points: Depends on `common.tst`, local callback fixtures, repository callback scripts, compiler tools, `mcdc_errs.dat`, and lcov/genhtml diagnostic wording.
- Risks: High brittleness from exact message greps, compiler-version coverage variance, permissions, and deliberately corrupt cache/config state; mitigated by targeted `--ignore` paths.
- Test signals: Passing signals are expected failure/success codes and greps for usage, callback, inconsistent, count, deprecated RC, empty diff, cache, context, and MC/DC messages.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/errs/msgtest.sh -->
