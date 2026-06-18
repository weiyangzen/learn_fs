# sources/object-store/minio-mc/cmd/alias-list.go

## Purpose

`alias-list.go` implements `mc alias list` / `ls`, showing one or all configured aliases from environment, custom maps, and persisted config.

## Important APIs, Types, and Functions

`aliasListCmd` defines the command. `mainAliasList` configures colors and prints aliases. `printAliases` aligns aliases and hides incomplete credentials. `byAlias` sorts messages. `buildAliasMessage` converts `aliasConfigV10` into output. `listAliases` gathers sources.

## Control Flow

The handler validates at most one alias, cleans it, gathers matching aliases, marks their operation as `list`, and prints them. Specific alias lookup uses `mustGetHostConfig`. Full listing reads environment variables with `mcEnvHostPrefix`, `aliasToConfigMap`, and persisted config, annotating config-file entries with source path, then sorts by alias.

## State and Persistence Behavior

The command reads local config and environment variables only. It does not mutate config.

## Dependencies and Integration Points

It integrates local alias config, environment alias expansion, global JSON mode, `aliasMessage`, and console table helpers.

## Risks and Edge Cases

Duplicate aliases from different sources can produce multiple rows. Non-JSON output pads the alias field by mutating the message. Credentials may be printed unless blanked because either access or secret key is missing.

## Test Signals

Tests should cover specific alias not found, source precedence/listing, sorted output, deprecated lookup field behavior, JSON versus table formatting, and incomplete credentials.
