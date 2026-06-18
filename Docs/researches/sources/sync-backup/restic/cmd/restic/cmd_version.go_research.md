# sources/sync-backup/restic/cmd/restic/cmd_version.go

Purpose: implements `restic version`, printing version and build runtime information.

Important APIs/types/functions: `newVersionCommand`; local `jsonVersion` struct.

Control flow and state: command does not open a repository. In JSON mode it encodes `message_type`, restic version, Go version, GOOS, and GOARCH; otherwise it prints a text line with the same runtime data.

Dependencies and integration points: uses `global.Version`, Go `runtime`, JSON encoder, terminal output, and progress printer for JSON encode errors.

Risks: JSON encode errors are printed but do not affect command return because cobra `Run` has no error return. Output is part of CLI compatibility.

Test signals: no direct tests in this shard; flags tests exercise command parsing.
