# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/SummarySubCommand.java

## Purpose
Implements `ozone admin namespace summary`, querying Recon for entity type and object counts under a namespace path.

## Important APIs, Types, And Functions
The command accepts a path, calls `/api/v1/namespace/summary` through `makeHttpCall`, parses response JSON with `JsonUtils`, and prints entity type plus count stats for volumes, buckets, directories, and keys when present.

## Control Flow
It rejects empty path, parses OFS input paths, calls Recon, handles null response and `PATH_NOT_FOUND`, then reads `countStats` and prints any count whose value is not `-1`.

## State And Persistence
Read-only against Recon namespace summary state.

## Dependencies And Integration Points
Depends on `NSSummaryAdmin`, `NSSummaryCLIUtils`, Recon REST, and Jackson `JsonNode`.

## Risks And Test Signals
It prints `summaryResponse.get("type")` directly, including JSON quoting for strings. Tests should cover all entity types, missing count fields, path-not-found, root/OFS paths, and null responses.
