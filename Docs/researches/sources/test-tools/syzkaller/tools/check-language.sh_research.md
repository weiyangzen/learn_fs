<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-language.sh -->
# sources/test-tools/syzkaller/tools/check-language.sh

## Purpose

Terminology lint for tracked source/docs/config files.

## Important APIs, Types, and Functions

Bash `nocasematch`, `git ls-files`, line-by-line `read`, regex checks for `slave`, `blacklist`, and `whitelist`, and suggestion strings.

## Control Flow

Filters tracked files, scans each line, ignores `bond_enslave`, chooses replacement suggestions, prints diagnostics and offending line, and exits non-zero on any match.

## State and Persistence Behavior

No persistence; stores counters and failure flag only.

## Dependencies and Integration Points

Requires bash and Git; part of presubmit policy checks.

## Risks and Edge Cases

Simple substring matching can false-positive in quoted/history/vendor text; exception list is hard-coded.

## Test Signals

Fixtures for each term, case variants, exception path/word, generated paths, and clean files.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-language.sh -->
