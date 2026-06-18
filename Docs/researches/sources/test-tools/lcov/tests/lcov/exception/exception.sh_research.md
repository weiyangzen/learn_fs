<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/exception/exception.sh -->
# sources/test-tools/lcov/tests/lcov/exception/exception.sh

- Purpose: Lcov exception branch filtering harness validating marker-based and option-based removal of exception branches, intermediate format needs, strict ordering, and filter combinations.
- Important APIs/types/functions: Procedural shell script using capture command forms, branch/filter options, `ENABLE_MCDC`, compiler gates, and common harness variables.
- Control flow: Compiles/runs `exception.cpp`, captures traces, checks branch counts, applies filters with and without markers, exercises ignore paths and strict ordering, and compares outputs.
- State and persistence behavior: Creates executable, coverage files, `.info`, logs, and filtered traces; clean removes them.
- Dependencies and integration points: Depends on lcov/geninfo branch capture, marker parser support, compiler coverage layout, and checked example data.
- Risks: Old compiler branch inconsistencies and intermediate-format requirements can change expected behavior.
- Test signals: Passing signals are expected branch count changes, marker diagnostics, and strict-ordering behavior matching greps/diffs.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/exception/exception.sh -->
