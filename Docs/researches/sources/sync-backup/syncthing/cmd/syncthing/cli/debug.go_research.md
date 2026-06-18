# sources/sync-backup/syncthing/cmd/syncthing/cli/debug.go

Purpose: implements `syncthing cli debug` subcommands for inspecting file index data and saving runtime profiles.

Important APIs/types/functions: `fileCommand`, `fileCommand.Run`, `profileCommand`, `profileCommand.Run`, and `debugCommand`.

Control flow: file debug normalizes the path, builds `debug/file?folder=...&file=...`, and pretty-prints the REST response. Profile debug accepts only `cpu` or `heap` and saves `debug/cpuprof` or `debug/heapprof` response content to the filename from `Content-Disposition`.

State and persistence: file command is read-only. Profile command writes the profile file supplied by the server response.

Dependencies/integration: uses REST API helpers in `utils.go`.

Risks and test signals: invalid profile type returns a local error. `saveToFile` trusts server-provided filename. No direct tests for command routing.
