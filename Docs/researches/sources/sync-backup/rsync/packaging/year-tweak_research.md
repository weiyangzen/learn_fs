
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/packaging/year-tweak -->
# Research: sources/sync-backup/rsync/packaging/year-tweak

## Purpose
`packaging/year-tweak` updates `latest-year.h` so the embedded latest copyright year matches the newest git-derived modification year among source files.

## Important APIs, Types, and Functions
The script's `main()` runs `support/git-set-file-times --list`, parses each output line for a year and filename, tracks the maximum year, reads `latest-year.h`, and rewrites it if the `#define LATEST_YEAR "YYYY"` line differs.

## Control Flow
It starts with `latest_year = '2000'`, streams command output from `subprocess.Popen`, regex-parses each line, exits on parse failure, waits for the subprocess, compares the generated one-line header content with the existing file, and writes only when changed.

## State and Persistence
The persistent output is `latest-year.h` in the current directory. It performs no backup. It depends on git-derived file times rather than wall-clock time.

## Dependencies and Integration Points
It depends on `support/git-set-file-times --list` and the format of its output. `release.py` invokes it during the tweak step after editing version/release files.

## Risks
The script does not check the subprocess return code, so a failing `git-set-file-times` that emits no parseable output could leave `latest_year` at `2000` or fail only on malformed lines. It assumes it is run from the rsync checkout root and that `latest-year.h` already exists.

## Test Signals
Use mocked `git-set-file-times --list` output to verify maximum-year selection, parse failures, unchanged-file behavior, and rewrite behavior. Release tests should check that `latest-year.h` changes when a newer source year is present.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/packaging/year-tweak -->
