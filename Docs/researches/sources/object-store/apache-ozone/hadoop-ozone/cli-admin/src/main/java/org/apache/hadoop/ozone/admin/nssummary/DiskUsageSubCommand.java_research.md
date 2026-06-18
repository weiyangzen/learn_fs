# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/DiskUsageSubCommand.java

## Purpose
Implements `ozone admin namespace du`, querying Recon for namespace disk usage and printing path totals and immediate subpath rows.

## Important APIs, Types, And Functions
Options include path, `--file`, `--replica`, `--no-header`, `ListLimitOptions`, and `PrefixFilterOption`. It calls `NSSummaryCLIUtils.makeHttpCall` against `/api/v1/namespace/usage`, parses JSON with `JsonUtils`, formats sizes with `FileUtils.byteCountToDisplaySize`, and prints aligned rows.

## Control Flow
The command rejects empty path, builds the Recon URL, calls Recon with parsed OFS path, handles null response and `PATH_NOT_FOUND`, prints optional header totals, then iterates `subPaths` up to limit and prefix filter, appending `/` to directory paths.

## State And Persistence
Read-only against Recon namespace summary state.

## Dependencies And Integration Points
Depends on `NSSummaryAdmin` for Recon address/security config, `NSSummaryCLIUtils`, Recon REST API, Ozone key prefix constants, list-limit and prefix-filter shell mixins.

## Risks And Test Signals
URL query parameters are appended without URL encoding. Prefix filtering happens client-side after Recon returns data. Tests should cover root path, OFS path parsing, path-not-found, empty objects, replica sizes, no-header, prefix filtering, file listing, and limit enforcement.
