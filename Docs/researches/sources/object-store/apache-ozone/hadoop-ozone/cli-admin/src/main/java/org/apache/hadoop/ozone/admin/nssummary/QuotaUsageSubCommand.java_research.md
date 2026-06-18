# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/QuotaUsageSubCommand.java

## Purpose
Implements `ozone admin namespace quota`, querying Recon for quota usage of a volume or bucket path.

## Important APIs, Types, And Functions
The command accepts a path, calls `/api/v1/namespace/quota`, parses `allowed` and `used`, and prints allowed, used, and remaining values with `FileUtils.byteCountToDisplaySize`.

## Control Flow
It rejects empty path, builds the Recon URL, calls Recon, handles null response, `PATH_NOT_FOUND`, and `TYPE_NOT_APPLICABLE`, then prints quota fields. `allowed == -1` is displayed as quota not set and remaining unknown.

## State And Persistence
Read-only against Recon namespace/quota summary state.

## Dependencies And Integration Points
Depends on `NSSummaryAdmin`, `NSSummaryCLIUtils`, Recon REST, `JsonUtils`, and `FileUtils`.

## Risks And Test Signals
It does not use `parseInputPath`, so OFS paths may be inconsistent with summary/du. It assumes `allowed` and `used` fields exist for applicable responses. Tests should cover unset quota, over-quota remaining calculation, type-not-applicable, path-not-found, and OFS path input.
