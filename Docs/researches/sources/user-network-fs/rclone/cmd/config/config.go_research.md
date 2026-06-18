<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/config/config.go -->
# sources/user-network-fs/rclone/cmd/config/config.go

## Purpose

`config.go` implements the `rclone config` command tree for interactive editing, file/path display, JSON dumps, provider listing, remote create/update/delete/password, OAuth reconnect/disconnect, user info, config encryption, and connection-string output.

## Important APIs, Types, and Functions

`init` registers all subcommands. Basic commands call `config.EditConfig`, `ShowConfigLocation`, `SaveConfig`, `ShowConfig`, `ShowRedactedConfig`, `Dump`, and `JSONListProviders`. `configCreateCommand` and `configUpdateCommand` parse key/value input with `argsToMap`, share `updateRemoteOpt`, and call `doConfig` to handle normal or non-interactive JSON output. `configPasswordCommand`, reconnect/disconnect, `configUserInfoCommand`, encryption set/remove/check, and `configStringCommand` wrap backend and config APIs.

## Control Flow

Most subcommands validate argument counts, parse or resolve remotes, then invoke config or backend feature functions. Non-interactive create/update returns a JSON `fs.ConfigOut`; interactive mode shows the resulting remote.

## State and Persistence Behavior

The file can create, update, delete, encrypt, decrypt, save, and display rclone config data. Reconnect and disconnect may mutate OAuth tokens or revoke credentials. Userinfo and string commands are read-only except backend auth side effects.

## Dependencies and Integration Points

It integrates Cobra, pflag, `fs/config`, `fs/rc.Params`, backend `Features().Disconnect/UserInfo`, `fs.ConfigFs`, JSON encoding, and command flag helpers.

## Risks and Test Signals

Risks include global `updateRemoteOpt` leakage across commands, cleartext password handling, redaction incompleteness, non-interactive protocol regressions, config encryption prompt behavior, and backend feature nil checks. Tests should cover `argsToMap`, create/update key parsing, non-interactive JSON, no-output, password obscuring flags, encryption check failures, disconnect/userinfo unsupported errors, and connection string formatting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/config/config.go -->
