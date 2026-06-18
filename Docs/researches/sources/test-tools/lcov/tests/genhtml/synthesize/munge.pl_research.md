<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/synthesize/munge.pl -->
# sources/test-tools/lcov/tests/genhtml/synthesize/munge.pl

- Purpose: Trace mutator injecting out-of-range line, function, and branch records to test synthesis of missing source metadata.
- Important APIs/types/functions: No subroutines; executable Perl filter from stdin to stdout over lcov `.info` records.
- Control flow: Line-oriented loop rewrites `LF/LH/FNH/FNF/BRF` counters and injects `DA`, `FN`, `FNDA`, and `BRDA` records.
- State and persistence behavior: No filesystem state directly; the harness redirects output to mutated traces.
- Dependencies and integration points: Depends on lcov info syntax and Perl regex processing; integrated by `synthesize.sh`.
- Risks: Intentional inconsistency can become invalid if parser validation changes.
- Test signals: Passing signal is downstream genhtml synthesis/warning behavior expected by `synthesize.sh`.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/synthesize/munge.pl -->
