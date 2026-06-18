# sources/test-tools/kdevops/scripts/ld-version.sh

## Purpose
`ld-version.sh` is an awk filter that extracts a linker version string from stdin and converts it into a single sortable numeric value.

## Important APIs, Types, And Functions
The awk script performs `gsub()` cleanup, `split($1,a,".")`, then prints `major*100000000 + minor*1000000 + patch*10000` and exits after the first input record.

## Control Flow
For the first line, it strips everything through a closing parenthesis, strips everything through `version `, strips suffixes after `-`, splits the first token on dots, prints the computed integer, and exits.

## State And Persistence
No state is persisted. Output depends only on the first line of linker version text.

## Dependencies And Integration Points
Depends on awk. Build scripts can pipe linker `--version` output into it for numeric version comparisons.

## Risks And Edge Cases
Missing patch components evaluate as zero in awk arithmetic. Non-GNU or unusual linker banners may not match the cleanup assumptions. Only the first input line is considered.

## Test Signals
Pipe sample GNU ld, gold, lld, version strings with suffixes, two-component versions, and malformed input; verify numeric output matches build comparisons.
