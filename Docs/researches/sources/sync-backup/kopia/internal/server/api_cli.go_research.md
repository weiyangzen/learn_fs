# sources/sync-backup/kopia/internal/server/api_cli.go

Purpose: implements the UI API endpoint that returns a reusable Kopia CLI command for the current server config.

Important APIs/types/functions: `handleCLIInfo` and `maybeQuote`.

Control flow: obtains `os.Executable`, falls back to `kopia`, quotes executable/config paths containing spaces, and returns `serverapi.CLIInfo` with `--config-file=...`.

State and persistence behavior: reads process executable path and server options; no mutation.

Dependencies and integration points: registered as `/api/v1/cli` by `Server.SetupHTMLUIAPIHandlers` and consumed by UI/client code.

Risks and test signals: quoting is minimal and only handles spaces. Tests validate returned command with a test server and repository config path.
