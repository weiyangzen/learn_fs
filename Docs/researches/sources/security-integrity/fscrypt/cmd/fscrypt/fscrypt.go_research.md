# sources/security-integrity/fscrypt/cmd/fscrypt/fscrypt.go

## Purpose
Program entry point for the `fscrypt` CLI. It configures templates, environment overrides, global flags, commands, and common command setup.

## APIs, Types, and Control Flow
`main` installs help templates, reads `FSCRYPT_CONF`, `FSCRYPT_ROOT_MNT`, and `FSCRYPT_CONSISTENT_OUTPUT`, creates a `cli.App`, sets version and usage handling, installs global flags, hides the help subcommand, registers top-level commands, recursively calls `setupCommand`, and runs the app. `setupCommand` wraps descriptions, appends universal flags, installs usage handlers, and sets `setupBefore` on leaf commands. `setupBefore` routes logs and normal output based on verbose/quiet. `defaultAction` shows help or returns a usage error.

## State, Dependencies, and Integration
Environment variables are critical for tests and alternate installations. `FSCRYPT_CONF` redirects action config, `FSCRYPT_ROOT_MNT` redirects login protector storage, and `FSCRYPT_CONSISTENT_OUTPUT` makes descriptor ordering stable.

## Risks and Test Signals
Environment overrides are process-global and affect all subsequent operations. Quiet mode discards normal output but errors still return through CLI. Only a trivial Go test exists; behavior is mostly covered by CLI tests.
