<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/synthesize/munge2.pl -->
# sources/test-tools/lcov/tests/genhtml/synthesize/munge2.pl

- Purpose: Trace mutator removing a line coverpoint for the first branch record to create branch-without-line data.
- Important APIs/types/functions: No subroutines; executable Perl filter from stdin to stdout over lcov `.info` records.
- Control flow: Tracks the first `BRDA` line, decrements `LF`, adjusts hit summaries, suppresses the matching `DA`, and passes other records through.
- State and persistence behavior: No filesystem state directly; the harness redirects output to mutated traces.
- Dependencies and integration points: Depends on lcov info syntax and Perl regex processing; integrated by `synthesize.sh`.
- Risks: Intentional inconsistency can become invalid if parser validation changes.
- Test signals: Passing signal is downstream genhtml synthesis/warning behavior expected by `synthesize.sh`.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/synthesize/munge2.pl -->
