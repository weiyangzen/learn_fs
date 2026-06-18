# sources/test-tools/xfstests-bld/fstests-bld/popt/testit.sh

Purpose: shell regression harness for popt test binaries. It runs `test1` with fixed argument combinations and compares full stdout to expected strings.

Important functions: `run` executes a program under `HOME=$builddir`, compares output exactly, and exits with code 2 on mismatch. `run_diff` exists for file-output tests but active `test3` calls are commented out.

Control flow: establishes `builddir`, changes to `srcdir`, then runs numbered test cases for basic options, aliases, rest handling, short options, POSIX modes, callbacks, exec aliases, one-dash long options, optional args, typed numeric conversions, `POPT_ARG_ARGV`, bit operations, bitsets, and exact `--usage`/`--help` text. Prints `Passed.` at the end.

State/persistence: temporary environment variables `POSIX_ME_HARDER` and `POSIXLY_CORRECT` are set/unset for specific cases. Temporary files from `run_diff` are removed if used. No persistent state except any logs from invoked programs.

Dependencies/integration: depends on compiled `test1`, `test-poptrc` in builddir/HOME, standard shell tools, `diff`, and deterministic terminal/help formatting.

Risks: exact string comparisons make tests fragile across locale, terminal width, binary prefix naming, and formatting changes. `run` uses backtick command substitution, which strips trailing newlines.

Test signals: high-value parser regression suite; failures identify specific numbered behaviors in popt core, config, help, and exec handling.
