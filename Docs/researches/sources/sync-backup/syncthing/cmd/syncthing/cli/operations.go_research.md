# sources/sync-backup/syncthing/cmd/syncthing/cli/operations.go

Purpose: implements operational REST commands for restart, shutdown, upgrade, folder override, and default ignore updates.

Important APIs/types/functions: `folderOverrideCommand`, `defaultIgnoresCommand`, `operationCommand`, parent `Run`, `folderOverrideCommand.Run`, and `defaultIgnoresCommand.Run`.

Control flow: parent `Run` maps restart/shutdown/upgrade to empty POSTs. Folder override loads config, verifies the folder ID exists, then POSTs `db/override`. Default ignores opens the supplied file through Syncthing filesystem abstraction, reads all lines, and PUTs `config/defaults/ignores`.

State and persistence: sends commands that can restart/shut down/upgrade the running daemon, override folder state, or change config defaults. Folder override is explicitly destructive.

Dependencies/integration: depends on REST API client, config structures, and filesystem abstraction.

Risks and test signals: the folder override implementation verifies the folder exists but posts `db/override` without including the folder ID in this file, so endpoint semantics must infer or this may be a bug depending on API expectations. No direct tests are present.
