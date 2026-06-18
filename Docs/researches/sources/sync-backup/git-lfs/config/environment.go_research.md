<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/environment.go -->
# sources/sync-backup/git-lfs/config/environment.go

## Research

`environment.go` defines the typed configuration access layer. `Environment` wraps a `Fetcher` and adds `Bool`, `Int`, `Int64`, and `All`; `EnvironmentOf` adapts any fetcher. Standalone conversion helpers parse booleans and integers, returning supplied defaults for blank or malformed numeric values.

Control flow is direct delegation: `Get`/`GetAll` forward to the fetcher, while typed methods fetch the raw string then call conversion helpers. State lives entirely in the underlying fetcher. Dependencies are `strconv` and `strings`. Integration points include OS, Git, map, delayed, URL, credential, filepath-filter, and filesystem configuration consumers. Risks are semantic compatibility: unknown boolean strings return `false` rather than the default, `Get` returns the fetcher’s last value convention, and `All` must be a defensive copy when the fetcher has mutable state. `environment_test.go` covers delegation, boolean truthy/falsy values, default handling, and integer parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/environment.go -->
