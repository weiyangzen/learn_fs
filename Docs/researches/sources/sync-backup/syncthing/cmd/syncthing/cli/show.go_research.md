# sources/sync-backup/syncthing/cmd/syncthing/cli/show.go

Purpose: implements read-only `syncthing cli show` commands.

Important APIs/types/functions: `showCommand` and `showCommand.Run`.

Control flow: selected subcommands call REST endpoints for version, config restart-required status, system status, connections, discovery cache, usage report, and nested pending commands.

State and persistence: read-only; pretty-prints JSON responses.

Dependencies/integration: depends on the API helper wrapper and Kong selected command names.

Risks and test signals: endpoint mappings are simple and therefore sensitive to REST path changes. No direct tests.
