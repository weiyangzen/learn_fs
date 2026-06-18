<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/extract.sh -->
# sources/test-tools/lcov/tests/lcov/extract/extract.sh

- Purpose: Comprehensive lcov capture/extract harness covering initial/all capture, external/internal files, unreachable tags, criteria/history/context callbacks, marker overrides, omit-lines, checksum validation, GCOV_PREFIX resolution, missing-source filtering, and filenames with spaces.
- Important APIs/types/functions: Procedural shell script using `LCOV_OPTS`, `CAPTURE`, compiler gates, filter variables, and helper scripts `fakeResolve.sh`, `history.sh`, `testContext.sh`, and `brokenCallback.pm`.
- Control flow: Compiles linked and unused sources, performs initial/current/all captures, lists and diffs outputs, validates callbacks/config/env expansion, checks marker errors, checksum mismatch, unreachable removal, separated gcno/gcda paths, and missing-source resolution.
- State and persistence behavior: Creates many `.info`, `.json`, `.log`, `.msg`, config files, executables, separated work directories, coverage data, and temporary files; the top cleanup block is the persistence boundary.
- Dependencies and integration points: Depends on common test harness, compilers, lcov/geninfo, checked gold list files, local helper callbacks, shell utilities, and filesystem permission/path behavior.
- Risks: Risks include compiler coverpoint count changes, unreadable-directory permissions, environment-variable config expansion, paths with spaces, and exact diagnostics.
- Test signals: Passing signals are gold list diffs, context JSON/comment fields, marker messages, omit-line counts, checksum failures, GCOV_PREFIX-equivalent traces, missing-source retain/remove checks, and space-containing filename capture.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/extract.sh -->
