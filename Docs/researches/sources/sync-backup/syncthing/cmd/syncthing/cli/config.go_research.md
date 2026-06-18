# sources/sync-backup/syncthing/cmd/syncthing/cli/config.go

Purpose: implements `syncthing cli config`, a reflection-driven configuration editor backed by the REST API.

Important APIs/types/functions: custom urfave/cli help templates, `configHandler`, `configCommand`, `configCommand.Run`, `configBefore`, and `configAfter`.

Control flow: `Run` builds a urfave CLI app to mimic Kong help, obtains an API client and current config, copies the original config, uses `recli` to construct commands over `config.Configuration`, and runs the nested app. `configBefore` permits help without requiring API connectivity. `configAfter` compares modified config to the original and POSTs `system/config` with indented JSON when changed.

State and persistence: reads current config via REST and persists changes through Syncthing's `system/config` endpoint.

Dependencies/integration: bridges Kong, urfave/cli, `recli`, Syncthing config structs, and the API client.

Risks and test signals: reflection exposes config surface based on struct tags, so tag changes can alter CLI behavior. Errors before command execution are deferred to allow help. No direct tests cover command construction or POST diffing.
