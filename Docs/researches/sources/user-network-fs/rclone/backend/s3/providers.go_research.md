# sources/user-network-fs/rclone/backend/s3/providers.go

## Purpose
S3 provider loader: embeds provider YAML and mutates S3 registration options/examples/quirks.

## Important APIs, Types, And Functions
Important surface: YamlMap, Quirks, Provider, addProvidersToInfo, loadProvider, loadProviders, constructProviders.

## Control Flow
loads provider/*.yaml, fatal-errors on missing/invalid Other, sorts AWS first and Other last, merges map examples and provider booleans into fs.Options

## State And Persistence
compile-time embedded YAML and runtime option descriptors.

## Dependencies And Integration Points
embed, yaml.v3, ordered-map, rclone fs.

## Risks And Test Signals
Risks and useful test signals: duplicate provider names, option-name switch drift, schema drift, fatal provider load failures.
