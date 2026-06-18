
# sources/sync-backup/kopia/tests/perf_benchmark/process_results.go

## Purpose
Parses benchmark output logs and emits CSV-style rows containing scenario, version, duration, CPU/RAM averages/maxima, and repository size.

## Important APIs, Types, And Functions
- Regexes `psrecordRegex` and `reposizeRegex` match `psrecord-<version>-(initial|second)-<scenario>.log` and `repo-size-<version>-<scenario>.log`.
- `processStats` stores duration, average/max CPU, and average/max RAM.
- `getProcessStats` scans psrecord logs, skipping the header and aggregating timestamp/CPU/RAM fields.
- `parseRepoSize` reads the first field from `du -bs` output.
- `main` scans current directory, stores only initial phase process stats, stores repo sizes, and prints CSV lines.

## Control Flow
The program walks `os.ReadDir(".")`, parses recognized files, populates nested maps by scenario/version, then prints one row per initial-process result with the matching repo size.

## State And Persistence Behavior
Read-only over current directory logs. Results are held in package-level maps and written to stdout.

## Dependencies And Integration Points
Depends on benchmark log naming from `perf-benchmark.sh`, psrecord text format with at least three whitespace fields per sample line, and `du -bs` output.

## Risks And Edge Cases
`repoSizeByScenarioArndVersion` contains a typo in the variable name but works. `getProcessStats` assumes every data line has enough fields; malformed or empty lines can panic. It ignores `second` phase psrecord logs entirely. Missing repo-size entries print zero without error because map lookup defaults to zero.

## Test Signals
Useful post-processing utility for benchmark artifacts; not a test itself.
