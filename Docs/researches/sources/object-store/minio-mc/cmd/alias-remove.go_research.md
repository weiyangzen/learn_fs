# sources/object-store/minio-mc/cmd/alias-remove.go

## Purpose

`alias-remove.go` implements `mc alias remove` / `rm`, deleting an alias from the local config file.

## Important APIs, Types, and Functions

`aliasRemoveCmd` declares the command. `checkAliasRemoveSyntax` validates exactly one alias. `aliasMustExist` checks configured aliases. `removeAlias` loads config, deletes the alias, saves config, and returns `aliasMessage`.

## Control Flow

The handler validates syntax, sets success color, calls `removeAlias`, marks the output operation as remove, and prints it.

## State and Persistence Behavior

The persisted local MinIO Client config is mutated by deleting the alias. The command does not contact the remote server.

## Dependencies and Integration Points

It depends on local config load/save helpers, alias validation, `mustGetHostConfig`, and shared alias output.

## Risks and Edge Cases

`aliasMustExist` may find aliases from sources other than the persisted config, but `removeAlias` only deletes from loaded config. That can produce surprising behavior for environment-provided aliases. Deletion is immediate and unconfirmed.

## Test Signals

Tests should cover missing alias, invalid alias, persisted alias deletion, env-only alias behavior, save failures, and output text/JSON.
