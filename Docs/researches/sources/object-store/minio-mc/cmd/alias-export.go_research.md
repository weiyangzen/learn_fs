# sources/object-store/minio-mc/cmd/alias-export.go

## Purpose

`alias-export.go` implements `mc alias export`, printing a stored alias configuration as JSON for reuse or import.

## Important APIs, Types, and Functions

`aliasExportCmd` defines the command. `checkAliasExportSyntax` validates exactly one alias and alias syntax. `exportAlias` loads the MinIO Client config and marshals the selected `aliasConfigV10`.

## Control Flow

The handler validates input, cleans the alias, loads config, looks up the alias in `Aliases`, marshals the config with color JSON, and prints it to stdout. Missing aliases fail with an invalid argument error.

## State and Persistence Behavior

The command reads local `mc` config only and writes stdout. It does not contact a server.

## Dependencies and Integration Points

It depends on config helpers such as `loadMcConfig`, `mustGetMcConfigPath`, alias validation helpers, `console.Println`, and `aliasConfigV10`.

## Risks and Edge Cases

Export includes secret keys in plaintext JSON. Environment-only or runtime alias overrides are not exported because the command reads the persisted config map.

## Test Signals

Tests should cover invalid aliases, missing aliases, JSON field preservation, and secret-bearing output expectations.
