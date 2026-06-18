<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/rc.go -->
# sources/user-network-fs/rclone/fs/config/rc.go

## Purpose
Registers Remote Control API endpoints for inspecting and mutating rclone configuration.

## Important APIs, Types, And Control Flow
Multiple `init` blocks register `config/unlock`, `config/dump`, `config/get`, `config/listremotes`, `config/providers`, `config/create`, `config/update`, `config/password`, `config/delete`, `config/setpath`, and `config/paths`. Handlers parse `rc.Params`, call config functions such as `CreateRemote`, `UpdateRemote`, `PasswordRemote`, `DeleteRemote`, `SetConfigPath`, and return JSON-shaped `rc.Params`. `rcConfig` handles backwards-compatible `obscure` and `noObscure` top-level flags and reshapes non-interactive `fs.ConfigOut`.

## State And Persistence
Handlers mutate global config storage and the selected config path. Create/update/password/delete may save config via lower-level helpers. Unlock changes process-local config password state.

## Dependencies And Integration Points
Integrates `fs.Registry`, `rc.Calls`, config storage, remote creation/update helpers, and OS temp/cache/config paths.

## Risks And Test Signals
Mis-shaped RC params return errors; legacy param names remain accepted. Risks include global config-path mutation and unintended persistence from remote mutation endpoints. Tests cover endpoint registration and representative CRUD, providers, paths, setpath, and unlock behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/rc.go -->
