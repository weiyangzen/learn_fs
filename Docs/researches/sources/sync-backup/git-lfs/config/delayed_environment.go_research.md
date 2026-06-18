<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/delayed_environment.go -->
# sources/sync-backup/git-lfs/config/delayed_environment.go

## Research

`delayed_environment.go` implements `delayedEnvironment`, an `Environment` wrapper that defers expensive Git config parsing until the first read. Its `Load` method is mutex-protected and idempotent; `Get`, `GetAll`, `Bool`, `Int`, `Int64`, and `All` all call `Load` before delegating to the realized environment.

The only state is the cached `env`, a mutex, and a callback supplied by `Configuration.NewIn` or `NewFrom`. This is the bridge between old code that expected `Configuration.loadGitConfig()` side effects and newer code that consumes an `Environment`. Dependencies are only `sync` and the local `Environment` interface. Risks include callback panics, callback returning nil, recursive load paths if the callback reads the same delayed environment, and stale cached config after repository config changes. It is tested indirectly by all configuration tests that use `cfg.Git`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/delayed_environment.go -->
