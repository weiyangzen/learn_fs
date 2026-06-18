# sources/test-tools/lcov/tests/perl2lcov/perltest1.sh

## Purpose

`perltest1.sh` verifies `perl2lcov` conversion from Devel::Cover databases, including empty-database errors, test names, namespace/function records, region and branch exclusions, checksums, empty-output handling, help/error behavior, LCOV summary compatibility, and genhtml compatibility.

## Important APIs, types, and functions

It runs `perl -MDevel::Cover=-db,cover_one,-coverage,statement,branch,condition,subroutine,-silent,1 example.pl`, `cover cover_one -silent 1`, `PERL2LCOV_TOOL`, `LCOV_TOOL --summary`, and `genhtml`. It checks `TN:`, `FNA:`, `DA:`, `BRDA:`, checksum-bearing `DA` records, `--filter region`, `--filter branch_region`, `--exclude`, `--ignore empty`, `--help`, and unsupported options.

## Control flow

The script resolves `LCOV_HOME`, cleans artifacts, runs the Perl fixture under Devel::Cover, first asserts that `perl2lcov` fails before `cover` post-processing with an "appears to be empty" error, then runs `cover` and converts successfully with test name `test1`. It validates function counts by namespace and the global function record, measures raw line/branch counts, compares counts after region and branch-region filters, verifies checksum format, tests exclusion of all input as both error and ignored-empty success, checks help and unsupported options, validates the generated info file with `lcov --summary`, renders it through genhtml under Devel::Cover, and converts genhtml's coverage database with ignored inconsistency.

## State and persistence behavior

It creates Devel::Cover databases `cover_one` and `cover_genhtml`, multiple `.info` files, logs, reports, XML/dat/json temporary files, and optional local coverage reports. Clean mode removes these.

## Dependencies and integration points

It depends on Perl, Devel::Cover, `cover`, `perl2lcov`, LCOV, genhtml, and the fixture `example.pl`. It integrates converter output with downstream LCOV summary and HTML reporting.

## Risks and test signals

The test is sensitive to Devel::Cover output shape and function indexing. Strong signals are expected empty-database failure, exact test name, namespace function counts, checksum presence, exclusion semantics, and downstream validation by LCOV/genhtml.
