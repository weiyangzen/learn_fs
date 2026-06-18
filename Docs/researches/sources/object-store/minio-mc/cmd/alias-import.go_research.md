# sources/object-store/minio-mc/cmd/alias-import.go

## Purpose

`alias-import.go` implements `mc alias import`, loading alias credentials from a JSON file or stdin and saving them into the local config.

## Important APIs, Types, and Functions

`aliasImportCmd` defines the command. `checkAliasImportSyntax` validates arg count and alias. `checkCredentialsSyntax` validates URL, access key, secret key, API signature, and path mode. `importAlias` saves the config and returns an `aliasMessage`.

## Control Flow

The handler validates syntax, chooses the credentials file path or stdin name, reads the JSON, unmarshals into `aliasConfigV10`, validates fields, loads existing config, writes the alias entry, saves config, and prints an import message.

## State and Persistence Behavior

This command mutates the local MinIO Client config file by adding or replacing an alias. It does not probe the remote server.

## Dependencies and Integration Points

It depends on local config load/save helpers, alias validation helpers, `aliasMessage`, and standard JSON/file IO.

## Risks and Edge Cases

Using `os.Stdin.Name()` as a read path for stdin may depend on platform behavior. Import overwrites an existing alias without confirmation. Credentials are validated syntactically but not verified against the server.

## Test Signals

Tests should cover file and stdin import, malformed JSON, invalid credential fields, overwrite behavior, and saved config contents.
