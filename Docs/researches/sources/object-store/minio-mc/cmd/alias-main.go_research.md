# sources/object-store/minio-mc/cmd/alias-main.go

## Purpose

`alias-main.go` defines the `mc alias` command group and the shared output type for alias operations.

## Important APIs, Types, and Functions

`aliasSubcommands` contains set, list, remove, import, and export. `aliasCmd` defines the group. `aliasMessage` carries alias URL, credentials, API, path, source, and deprecated lookup fields. `aliasMessage.String` and `JSON` render operation results.

## Control Flow

The group action reports command-not-found help. Subcommands create `aliasMessage` values with operation names that select list/add/set/remove/import rendering.

## State and Persistence Behavior

The file itself only defines command and message structures. Persistence is handled by alias subcommands through config helpers.

## Dependencies and Integration Points

It integrates the alias command family into the app command tree and is reused by alias set/list/remove/import.

## Risks and Edge Cases

`aliasMessage.JSON` can include secret keys. The deprecated `Lookup` field is still supported for compatibility with older output consumers.

## Test Signals

Tests should verify group command behavior, JSON status injection, list rendering with path/lookup fallback, and success text per operation.
