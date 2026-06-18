<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/ui_test.go -->
# sources/user-network-fs/rclone/fs/config/ui_test.go

## Purpose
External-package scripted tests for the interactive config UI and programmatic remote update/password helpers.

## Important APIs, Types, And Control Flow
`testConfigFile` installs temp configfile storage, redirects stdout, registers a fake backend, and restores global config. `makeReadLine` feeds scripted answers. Tests cover `NewRemote`, `RenameRemote`, `DeleteRemote`, `ChooseOption`, generated passwords, `NewRemoteName`, `CreateRemote`, `UpdateRemote`, `PasswordRemote`, and required/default/multiple-choice/exclusive option semantics.

## State And Persistence
The tests create temporary config files, mutate global `config.ReadLine`, `config.Password`, `fs.ConfigInfo`, environment variables for config keys, and the global config storage, then restore them.

## Dependencies And Integration Points
Uses configfile storage, obscure codec, fake `fs.RegInfo` backend options, RC parameter maps, and testify.

## Risks And Test Signals
Good signal for user-facing config prompts without an actual terminal. Because stdout is nil and assertions focus on stored values, prompt formatting regressions may pass unnoticed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/ui_test.go -->
