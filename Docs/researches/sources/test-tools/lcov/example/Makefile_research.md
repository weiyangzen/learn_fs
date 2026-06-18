# sources/test-tools/lcov/example/Makefile Research

Purpose: this Makefile builds and exercises the LCOV example C program, captures several coverage traces, generates HTML reports, and demonstrates differential coverage and review workflows.

Important targets and variables: `CC`, `CFLAGS`, `LDFLAGS`, `LCOV_FLAGS`, `LCOV_HOME`, `EG_SRCDIR`, `REPO`, `BINDIR`, `SCRIPTS`, `SCRIPTDIR`, `LCOV`, `GENHTML`, `GENDESC`, `GENPNG`, and `GITDIFF` locate tools and configure coverage. Targets include `example`, object builds, `output`, `descriptions`, `all_tests`, `test_noargs`, `test_2_to_2000`, `test_overflow`, `test_differential`, and `clean`.

Control flow: the default `all` target builds `output`. Compilation uses GCC coverage flags and may add GCC 14 MC/DC flags. Basic test targets zero counters, run the example with different arguments, and capture `.info` files. `output` combines traces into flat and hierarchical `genhtml` reports. `test_differential` creates a temporary git repo, commits baseline sources, builds/runs tests, captures baseline coverage with version data, swaps modified sources, captures current coverage, creates a git diff, then generates differential and review reports with annotate, version, select, history, and profile scripts.

State and persistence: writes objects, executable, `.gcno/.gcda`, trace `.info`, descriptions, output directories, hierarchical reports, and `exampleRepo`.

Dependencies and integration: requires GCC, git, LCOV bin scripts, support scripts, Perl for version checks and optional Devel::Cover wrapper, and optionally `genpng`/GD for frames.

Risks: `CXX` is used for version detection without a default. `test_overflow` intentionally tolerates failure. Git commits require configured user identity. The shell uses Bash arrays under `$(shell)`, so non-Bash make shells can break MC/DC detection.

Test signals: run default output, individual test targets, `test_differential`, `LCOV_HOME` override, old GCC branches, GCC 14 MC/DC branch, missing `genpng`, and `COVER_DB` Perl coverage instrumentation.
