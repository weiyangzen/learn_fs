# sources/test-tools/syzkaller/tools/syz-reporter/reporter.go

## Purpose
`syz-reporter` builds an HTML crash summary for a syzkaller manager workdir and opens it in a browser. It is intended for inspecting crash/reproducer results, especially after `syz-crush` style runs.

## Important APIs, types, and functions
- `UISummaryData`, `UICrashType`, and `UICrash` are template view models.
- `main` loads a manager config, creates a temporary HTML filename, renders `httpSummary`, writes it, and starts `xdg-open`.
- `httpSummary` collects crashes, counts crash types and crash types with reproducers, and executes `summaryTemplate`.
- `collectCrashes` lists `workdir/crashes`, calls `readCrash`, and sorts by lowercase description.
- `readCrash` reads crash metadata including description, log indices, tags/prog reproducers, cause/fix commits, and cause config data.
- `trimNewLines` removes trailing newline bytes.

## Control flow
The crash directory is scanned by 40-character crash IDs. Each crash type's description is required; missing/empty descriptions skip the entry. File names drive classification: `logN` adds a crash record, `tag*` and `*prog` add reproducers, `cause.commit`, `fix.commit`, and `kconfig.CauseConfigFile` populate metadata. The template renders sortable columns.

## State and persistence behavior
Reads manager config and workdir crash files. Writes a temporary `.html` file and launches a browser. It does not modify crash data. The temporary file is not removed by the process after opening.

## Dependencies and integration points
Uses `pkg/mgrconfig`, `pkg/osutil`, `pkg/kconfig`, and `pkg/html/pages`. It expects the manager crash store on disk but does not reuse `manager.CrashStore` yet.

## Risks and edge cases
In `main`, `if httpSummary(buf, cfg) != nil { log.Fatalf("%v", err) }` logs the wrong `err` variable instead of the render error. Crash log contents are not loaded into `UICrash` despite fields existing. Reproducer map iteration order is nondeterministic in the template. Cause config lists longer than ten are collapsed to `...`.

## Test signals
No direct tests. Good tests would construct temporary crash directories and assert rendered counts, metadata extraction, sorting, malformed ID skipping, and the error variable bug.
