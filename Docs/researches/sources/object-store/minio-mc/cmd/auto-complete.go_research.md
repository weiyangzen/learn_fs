# sources/object-store/minio-mc/cmd/auto-complete.go

## Purpose

`auto-complete.go` builds shell completion support for `mc` commands, including filesystem paths, S3 paths, aliases, and admin config keys.

## Important APIs, Types, and Functions

Predictor types are `fsComplete`, `adminConfigComplete`, `s3Complete`, and `aliasComplete`. Key helpers are `completeAdminConfigKeys`, `completeS3Path`, `flagsToCompleteFlags`, `cmdToCompleteCmd`, and `mainComplete`. `completeCmds` maps command paths to predictors.

## Control Flow

Filesystem completion delegates to `posener/complete`, with special handling for `~/`. S3 completion loads config, predicts aliases until a slash is present, then lists remote path contents and recurses into a single matching directory. Admin config completion predicts aliases and config keys from `HelpConfigKV`. `cmdToCompleteCmd` recursively converts `cli.Command` trees into `complete.Command`, skipping hidden subcommands and adding aliases. `mainComplete` builds the root completion tree from `appCmds` and runs the completion engine.

## State and Persistence Behavior

The code reads local config and may contact remote S3/admin endpoints for path and config-key predictions. It writes no persistent state.

## Dependencies and Integration Points

It integrates with the full CLI command tree, `posener/complete`, local config loading, `newClient`, `newAdminClient`, object listing, admin config help APIs, global flags, and many command path names.

## Risks and Edge Cases

Completions can trigger network calls and may be slow or fail silently. The `completeCmds` map must stay synchronized with visible leaf commands. S3 recursive completion can expand into remote listings when exactly one directory matches. Hidden commands are skipped in command conversion.

## Test Signals

Tests should verify command coverage, flag conversion for long and short flags, hidden command skipping, alias completion sorting, tilde restoration, deep-level stopping, and graceful nil predictions on config/client failures.
