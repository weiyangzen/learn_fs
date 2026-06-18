## sources/sync-backup/restic/internal/global/secondary_repo.go

Purpose: option handling for commands that need a second/source repository, including current `from-*` flags and deprecated `repo2` flags.

Important APIs/types: `SecondaryRepoOptions` stores explicit password plus current and legacy repo, repository-file, password-file, password-command, key-hint, and insecure-no-password options. `AddFlags` registers deprecated/hidden legacy flags, current source flags, and environment defaults. `FillGlobalOpts` validates option groups, overlays selected secondary options onto a copy of global `Options`, resolves password with the appropriate env variable, prompts if needed, and returns whether current `from-*` options were used.

Control flow and state: empty options are rejected. Current and legacy groups are mutually exclusive. For current options, `--from-repo` conflicts with `--from-repository-file` and can carry `from-insecure-no-password`; for legacy `repo2`, insecure empty password remains disabled for compatibility. Explicit `SecondaryRepoOptions.Password` wins over resolving file/command/env.

Dependencies and integration points: builds on `resolvePassword` and `readPassword` from `global.go`; uses pflag for CLI integration and restic errors. Commands can pass the returned `Options` to normal repository open paths.

Risks and test signals: migration from `repo2` to `from-*` is compatibility-sensitive. Password-command execution and file reading inherit risks from global password resolution. Tests cover valid current/legacy flows, file/command password sources, no-repo failures, mutually exclusive source fields, missing password files, invalid commands, and mixed option groups.
