# sources/sync-backup/syncthing/cmd/syncthing/cli/main.go

Purpose: defines the top-level `syncthing cli` command tree and stdin command loop.

Important APIs/types/functions: `CLI`, `Context`, `CLI.AfterApply`, `stdinCommand`, and `stdinCommand.Run`.

Control flow: `AfterApply` creates an `apiClientFactory` from global `--gui-address` and `--gui-apikey` flags and binds it into the Kong context. `stdinCommand` reads shell-quoted command lines from stdin, parses each into a fresh CLI parser, runs it, prints per-command errors, and continues.

State and persistence: no direct state beyond context binding. Stdin mode repeatedly invokes command handlers that may read/write the Syncthing REST API.

Dependencies/integration: ties together `show`, `debug`, `operations`, `errors`, `config`, and stdin subcommands with Kong and shellquote parsing.

Risks and test signals: stdin mode ignores the original top-level `cli -` prefix and parses input directly as CLI subcommands. It prints errors instead of aborting per command. No direct tests.
