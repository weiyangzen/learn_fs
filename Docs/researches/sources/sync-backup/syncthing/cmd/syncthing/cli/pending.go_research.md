# sources/sync-backup/syncthing/cmd/syncthing/cli/pending.go

Purpose: implements `syncthing cli show pending` subcommands.

Important APIs/types/functions: `pendingCommand` and `pendingCommand.Run`.

Control flow: dispatches `devices` to `cluster/pending/devices`; dispatches `folders` to `cluster/pending/folders`, optionally adding a `device` query parameter.

State and persistence: read-only REST access to pending cluster state.

Dependencies/integration: nested under `showCommand` and uses `indexDumpOutputWrapper`.

Risks and test signals: command depends on Kong selected-name matching. No direct tests cover query encoding.
