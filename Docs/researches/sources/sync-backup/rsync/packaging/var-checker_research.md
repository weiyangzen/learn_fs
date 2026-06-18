
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/packaging/var-checker -->
# Research: sources/sync-backup/rsync/packaging/var-checker

## Purpose
`packaging/var-checker` is a Python maintenance checker for rsync C sources. It reports extraneous `extern` declarations, variables defined but apparently unused, and inconsistent types or array sizes across files.

## Important APIs, Types, and Functions
- Regexes `VARS_RE` and `EXTERNS_RE` find candidate file-scope variables and extern declarations.
- Global dictionaries `types` and `sizes` track cross-file declarations by variable name.
- `main()` locates the source directory, loads helper C files for special test sources, scans all `*.c`, and reports one-reference variables/externs.
- `slurp_file()` reads a file and can strip extern declarations.
- `parse_vars()` normalizes declarations, splits multiple declarators, checks type/size consistency, and returns variable names.

## Control Flow
The script changes to the parent directory if invoked from `packaging/`, reads `syscall.c` and `util1.c` as supplemental text for specific test files, then processes each C file. It parses variable and extern candidate lines, appends supplemental helper text where needed, rewrites macro names that would otherwise confuse usage search, constructs a combined variable-name regex, counts occurrences, and prints variables or externs that occur only in their declaration.

## State and Persistence
It has no file-writing side effects. Cross-file type and size observations persist in module dictionaries for the duration of the run.

## Dependencies and Integration Points
It depends on Python stdlib and rsync C source naming conventions. It is a developer hygiene tool, not part of the runtime build. It integrates with the source tree by assuming `syscall.c` marks the top-level directory.

## Risks
Regex-based C parsing can produce false positives/negatives for complex declarations, macros, function pointers, comments, conditional compilation, or generated uses. The occurrence count treats textual matches as uses and has special-case rewrites for only a few macros. It reports to stdout without structured status.

## Test Signals
Run it before releases or variable refactors and review output manually. Fixture C snippets should cover multiple declarators, pointers, arrays, initialized variables, externs, macro references, and inconsistent declarations.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/packaging/var-checker -->
