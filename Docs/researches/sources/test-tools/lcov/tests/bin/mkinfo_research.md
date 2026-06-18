# sources/test-tools/lcov/tests/bin/mkinfo

Purpose: deterministic-ish fixture generator for fake lcov coverage data and optional source trees. It creates full, target, partial, and zero coverage `.info`/`.counts` files used by LCOV regression tests.

Important APIs: configuration helpers `read_config`, `apply_config`, `get_value`, `get_int`, `get_list`; generation helpers for filenames, lines, functions, branch distributions, source structures, hits, filters, splitting, and writing; `main` handles CLI `mkinfo <config_file> [-o output_dir] [--seed seed] [section.key=value...]`.

Control flow and persistence: after parsing config and seeding `rand`, it generates a random source model with files, instrumented lines, functions, and branches; optionally writes blank source files under `-o`; creates random full hit data; writes `full.info/counts`; reduces hits to target coverage and writes `target`; splits hits into complementary `part1`/`part2`; zeroes all hits and writes `zero`. Count files summarize aggregate hit/found totals for validation.

Dependencies and integration: invoked by `common.mak` `prepare` to create `ZEROINFO`, `FULLINFO`, `TARGETINFO`, `PART1INFO`, and `PART2INFO`. Uses Perl stdlib `Getopt::Long`, `Cwd`, `File::Path`, `File::Basename`, and `Data::Dumper`.

Risks and test signals: random generation can create odd edge cases, controlled by `--seed`. Branch hit sanitization encodes lcov rule that untaken blocks use `-`. Tests depend heavily on output consistency; `check_counts` and downstream lcov/genhtml tests are the main validators.
