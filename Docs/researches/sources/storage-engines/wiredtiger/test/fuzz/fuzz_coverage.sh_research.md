# sources/storage-engines/wiredtiger/test/fuzz/fuzz_coverage.sh

Purpose: post-processes clang fuzzing coverage data into text and HTML reports for a fuzz target.

Important commands and variables: accepts `<fuzz-test-binary>`, uses `PROFDATA_BINARY` or `llvm-profdata`, uses `COV_BINARY` or `llvm-cov`, merges `*.profraw` into `<binary>_cov.profdata`, and writes `<binary>_cov.txt` plus `<binary>_cov.html`.

Control flow: validates an argument, resolves tool binaries with defaults and informational messages, removes previous coverage outputs, checks for `.profraw` files, exits with guidance if none exist, runs `llvm-profdata merge -sparse`, then runs `llvm-cov show` twice for text and HTML output.

State and persistence: deletes previous `*_cov.profdata`, `*_cov.txt`, and `*_cov.html` in the current directory, reads all `.profraw`, and writes new coverage artifacts next to the run outputs.

Dependencies and integration: intended after `fuzz_run.sh` in a build configured with `-fprofile-instr-generate` and `-fcoverage-mapping`. Requires clang coverage tools compatible with the compiler output.

Risks and test signals: wildcard cleanup is scoped only by current directory naming, so callers must run it in the fuzz output directory. Missing `.profraw` or tool command failures produce non-zero exits.
