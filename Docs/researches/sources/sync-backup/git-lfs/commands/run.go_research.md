<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/run.go -->
# sources/sync-backup/git-lfs/commands/run.go

## Research

`run.go` builds and executes the root `git-lfs` Cobra command. `NewCommand` attaches a default HTTP logging `PreRun`; `RegisterCommand` stores command factory callbacks under a mutex; `Run` initializes translation, root/help/completion commands, canonicalizes environment, creates global `cfg`, attaches all registered commands, and returns `0` or `127`.

The control flow is mostly command assembly. Shell completion generation has custom bash and zsh rewrites so completion works when invoked as `git lfs`. Help and usage are backed by generated `ManPages` content. `setupHTTPLogger` creates `cfg.LocalLogDir()/http/http-<unix>.log` when `GIT_LOG_STATS` is set and wires the API client to record HTTP stats. State is global package state: command registrations, `rootVersion`, and `cfg`. Integration points include every command package `init`, Cobra, generated man content, translation, filesystem config, and the API client. Risks include global initialization order, concurrent registration, completion string patch drift after Cobra changes, and log creation before repository config is usable. Test signals are mainly CLI/integration tests for help, completion, version, and HTTP stat logging.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/run.go -->
