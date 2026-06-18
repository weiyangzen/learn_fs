<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/fakeResolve.sh -->
# sources/test-tools/lcov/tests/lcov/extract/fakeResolve.sh

- Purpose: Resolve helper for separated gcno/gcda extraction tests; echoes its first argument unchanged.
- Important APIs/types/functions: Executable `/bin/sh` script with `printf '%s\n' "$1"` behavior.
- Control flow: Called by lcov `--resolve-script` to provide a deterministic resolved path.
- State and persistence behavior: No persistent state; stdout only.
- Dependencies and integration points: Depends on `/bin/sh` and lcov resolve-script invocation.
- Risks: Assumes the first argument is the desired path.
- Test signals: Passing signal is `resolve.info` matching the reference trace.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/fakeResolve.sh -->
