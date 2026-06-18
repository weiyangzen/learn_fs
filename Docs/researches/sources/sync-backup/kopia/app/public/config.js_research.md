# sources/sync-backup/kopia/app/public/config.js

## Purpose
Manages KopiaUI repository configuration discovery and in-memory repository list state in the Electron main process.

## APIs, Functions, and Control Flow
The module dynamically imports Node `fs`, `path`, Electron, and `electron-log`; `log` is imported but unused. `portableConfigDirs()` returns candidate portable repository directories from `KOPIA_UI_PORTABLE_CONFIG_DIR`, app-relative macOS paths, and executable-relative non-macOS paths. `globalConfigDir()` lazily chooses the first existing portable directory, marks `isPortable`, or falls back to Electron `appData/kopia`. `loadConfigs()` creates the directory with mode `0700`, scans for files ending in `.config`, stores repo IDs in `configs`, and creates a default `repository` entry with `firstRun=true` when none exist.

## State and Persistence
Persistent state is the config directory and `*.config` files shared with the Kopia CLI. In-memory state includes `configs`, `myConfigDir`, `isPortable`, and `firstRun`. IPC handler `config-list-fetch` emits `config-list-updated-event` with all repo IDs. `deleteConfigIfDisconnected(repoID)` removes non-default in-memory repo IDs if their config file no longer exists. `configForRepo(repoID)` ensures an ID exists in memory and emits an update, but returns the preexisting value, so it returns `undefined` for newly added IDs.

## Risks and Test Signals
The `addNewConfig()` check `if (!configs)` never triggers because `configs` starts as `{}`, so the first manually added repo gets a timestamped ID rather than `repository`; `loadConfigs()` handles the default path separately. Lazy global directory selection means environment and app path must be stable before first use. Test signals come from UI/E2E flows that create, list, disconnect, and delete repository configurations.
