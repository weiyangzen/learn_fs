# sources/test-tools/syzkaller/tools/syz-symbolize/symbolize.go

## Purpose
`syz-symbolize` symbolizes kernel crash logs and can save parsed crashes in syzkaller crash-store format.

## Important APIs, types, and functions
- Flags configure target OS/arch, kernel object/source directories, output crash directory, or a partial manager config.
- `main` builds/loads a partial manager config, completes kernel dirs, creates a `report.Reporter`, reads the input log, parses all reports, symbolizes them, prints metadata and reports, and optionally calls `saveCrash`.
- `saveCrash` hashes the report title to create a crash directory and writes `description`, `log`, and optional `report` files.

## Control flow
If `report.ParseAll` finds no structured reports, the whole input is wrapped in `report.Report` and symbolized in place, then printed. Otherwise each parsed report can be saved before symbolization, then symbolized and printed with title, corruption/suppression status, and maintainer recipients.

## State and persistence behavior
Reads config or flag-derived kernel paths and one log file. Writes symbolized output to stdout. With `-outdir`, creates crash directories and files named by title hash.

## Dependencies and integration points
Integrates with `pkg/report` parsing/symbolization, `pkg/mgrconfig` partial config loading, `pkg/vcs` maintainer recipient formatting, and `pkg/hash`/`pkg/osutil` for crash persistence.

## Risks and edge cases
Saving occurs before symbolization, so saved `report` content may be unsymbolized while stdout is symbolized. Hashing only the title groups same-title crashes. If no report is parsed, `-outdir` is ignored. Maintainer extraction depends on reporter/kernel source availability.

## Test signals
No direct tests here. Useful cases include no parsed report fallback, multiple reports in one log, outdir crash-store layout, config vs flag path config, and symbolization failures.
