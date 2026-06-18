<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/synthesize/synthesize.sh -->
# sources/test-tools/lcov/tests/genhtml/synthesize/synthesize.sh

- Purpose: Genhtml synthesis regression harness for inconsistent trace data, including out-of-range lines and branches without line coverpoints.
- Important APIs/types/functions: Procedural shell script using common harness variables, local mutators `munge.pl` and `munge2.pl`, compiler tools, lcov, and genhtml.
- Control flow: Compiles/captures data, normalizes compiler differences, mutates traces, runs genhtml with source/filter options, and greps for synthesized labels or their absence.
- State and persistence behavior: Creates mutated `.info` files, logs, executable/coverage files, and report directories; cleanup removes them.
- Dependencies and integration points: Depends on `common.tst`, Perl mutators, gcc/gcov/lcov/genhtml, and stable synthesized-coverpoint wording.
- Risks: Intentional trace inconsistency and compiler-version differences require ignore categories and normalization.
- Test signals: Passing signals are expected generated labels, absence of prohibited labels, and successful branch-without-line handling.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/synthesize/synthesize.sh -->
