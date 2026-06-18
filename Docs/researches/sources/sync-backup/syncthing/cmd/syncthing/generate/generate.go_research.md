# sources/sync-backup/syncthing/cmd/syncthing/generate/generate.go

Purpose: implements `syncthing generate`, creating or updating keys and config without starting the daemon.

Important APIs/types/functions: `CLI`, `CLI.Run`, `Generate`, and `updateGUIAuthentication`.

Control flow: `Run` optionally reads GUI password from stdin when `--gui-password=-`, then calls `Generate` for the config base directory. `Generate` expands the directory, ensures it exists, sets locations, loads or creates certificate/key files, calculates device ID, loads existing config or creates default config, starts config wrapper service, optionally updates GUI username/password, waits for modification, and saves config.

State and persistence: creates or reuses cert/key files, creates config directory, creates or modifies `config.xml`, and writes password hashes through config GUI helpers.

Dependencies/integration: uses Syncthing config, events, filesystem, locations, protocol device IDs, and `lib/syncthing` certificate/default config helpers.

Risks and test signals: existing keys are intentionally not overwritten. Password read from stdin reads one line only. Config wrapper is transient but required for safe modification. No direct tests in this subset.
