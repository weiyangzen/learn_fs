# sources/sync-backup/syncthing/cmd/infra/ursrv/main.go

Purpose: top-level command entrypoint for the usage reporting server `ursrv`.

Important APIs/types/functions: `CLI` contains a default `Serve serve.CLI` subcommand. `main` configures text `slog`, logs build version information, parses commands with Kong, and runs the selected command.

Control flow: startup is intentionally thin: logging setup, version log, parse, run, fatal log on command failure. All server behavior is delegated to `cmd/infra/ursrv/serve`.

State and persistence: no direct state or persistence; it passes through to the `serve` package.

Dependencies/integration: depends on Kong, `slog`, Syncthing `build`, and the local `serve` package.

Risks and test signals: failure handling uses `log.Fatalf`, which exits immediately. There are no direct tests; coverage lives in the serve package tests.
