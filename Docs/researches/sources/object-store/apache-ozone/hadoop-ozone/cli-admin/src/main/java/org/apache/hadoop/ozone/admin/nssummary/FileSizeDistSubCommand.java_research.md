# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/FileSizeDistSubCommand.java

## Purpose
Implements `ozone admin namespace dist`, querying Recon for file-size distribution under a namespace path.

## Important APIs, Types, And Functions
The command accepts a required-ish path, calls `/api/v1/namespace/dist`, parses `dist` JSON bins, converts bin indexes to byte ranges using powers of two, and prints percentage/count rows.

## Control Flow
It rejects empty path, calls Recon, handles null response, `PATH_NOT_FOUND`, and `TYPE_NOT_APPLICABLE`, sums distribution bins, prints an empty-object message when all bins are zero, and prints non-zero bins as readable ranges.

## State And Persistence
Read-only against Recon namespace summary data.

## Dependencies And Integration Points
Depends on `NSSummaryAdmin`, `NSSummaryCLIUtils`, Recon REST, `JsonUtils`, and `FileUtils`.

## Risks And Test Signals
This command passes `path` directly rather than `parseInputPath`, unlike summary/du, so OFS paths may behave differently. Tests should cover OFS paths, empty distribution, type-not-applicable, non-zero bins, and percentage rounding.
