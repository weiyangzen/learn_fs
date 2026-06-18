# sources/test-tools/lcov/bin/perl2lcov Research

Purpose: `perl2lcov` is an executable Perl translator from Devel::Cover coverage databases to LCOV tracefile format. It consumes one or more post-processed Devel::Cover DB directories, applies the standard LCOV utility option layer, and writes `perlcov.info` or `--output`.

Important APIs and functions: `print_usage` supplies the lcovutil help text. `findPackage($extents, $line)` binary-searches sorted package/subroutine extent lists to find the last declaration before a line. The script relies heavily on `Devel::Cover::DB`, `Devel::Cover::Truth_Table`, and LCOV Perl classes imported through `lcovutil`, especially `TraceFile`, `BranchBlock`, and `BranchElement`.

Control flow: after enabling branch/function coverage globals and parsing common options, it creates one `TraceFile`, iterates each input DB, validates non-empty cover items, then iterates source files. For each file it collects statement, branch, condition, and subroutine criteria, optionally greps the source for `package` and `sub` declarations, appends DA line counts, creates function definitions/counts, prefers condition truth-table branch records over simple branch data, unions test maps into summary maps, derives and corrects function end lines, applies filters/comments, writes the tracefile, and exits nonzero when coverage criteria fail.

State and persistence: persistent output is the LCOV `.info` file. In-memory state includes package/function extents, per-test maps, branch blocks, comments, filters, and global coverage flags in `lcovutil`.

Dependencies and integration: this is part of the LCOV bin suite and integrates with common lcovutil options such as substitution, exclusion, checksum, comments, version scripts, filters, and coverage criteria. It depends on `grep` for source declaration scanning.

Risks: Devel::Cover data can be internally inconsistent, so the script uses ignorable errors for empty, unsupported, source, unknown-category, and inconsistent-data cases. Branch expression reconstruction from truth tables is approximate. The `grep` parser only handles simple declaration syntax. Missing source files limit checksum and function extent quality.

Test signals: useful tests are Devel::Cover DBs with statement-only data, branch and condition data, multiple packages per file, anonymous/BEGIN subroutines, missing source files, exclusions/substitutions, and coverage-criteria failure paths.
