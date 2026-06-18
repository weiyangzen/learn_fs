<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/ui.go -->
# sources/user-network-fs/rclone/fs/config/ui.go

## Purpose
Implements rclone's textual interactive configuration UI for creating, editing, copying, renaming, deleting, displaying, and password-protecting remotes.

## Important APIs, Types, And Control Flow
Input helpers include `ReadLine`, `ReadNonEmptyLine`, `CommandDefault`, `Confirm`, `Choose`, `Enter`, `ChoosePassword`, and `ChooseNumber`. Remote operations include `ShowRemotes`, `ChooseRemote`, `ShowRemote`, `ShowRedactedRemote`, `OkRemote`, `NewRemoteName`, `NewRemote`, `EditRemote`, `DeleteRemote`, `RenameRemote`, `CopyRemote`, `ShowConfig`, `ShowRedactedConfig`, and `EditConfig`. Backend configuration loops through `fs.BackendConfig` states, prompting for `fs.Option` values via `ChooseOption`, then calls create/update/post-config helpers. Password functions validate UTF-8, trim warnings, NFKC-normalize, double-enter confirmation, and toggle config encryption.

## State And Persistence
Uses global `ReadLine`, buffered stdin state, global loaded config data, config encryption key state, and `SaveConfig`. Remote create/edit/delete/rename/copy persist through config storage; display functions only print.

## Dependencies And Integration Points
Integrates terminal/liner input, backend registry, configmap/configstruct conversion, obscure password storage, drive-letter and config-name validation, and filesystem `ConfigInfo` for auto-confirm.

## Risks And Test Signals
Interactive loops can fatal on input errors and mutate global state. Sensitive output is redacted only when backend options mark fields password/sensitive. Tests script `ReadLine` to cover CRUD, option parsing, required/default choice rules, password generation, and exclusive examples.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/ui.go -->
