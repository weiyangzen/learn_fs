# sources/object-store/minio-mc/cmd/share-main.go

## Purpose
Defines the top-level `mc share` command, subcommand registration, and migration cleanup for legacy share storage.

## Important APIs, types, and functions
- `shareSubcommands` contains `shareDownload`, `shareUpload`, and `shareList`.
- `shareCmd` registers command metadata and hides the help subcommand.
- `migrateShare` deletes the legacy `urls.json` file from the share directory if present.
- `mainShare` reports missing/unknown subcommands via `commandNotFound`.

## Control flow
The top-level command does not perform share generation. Subcommands own their execution. `migrateShare` is intended to run during configuration migration: if the share directory exists and old `urls.json` exists, it removes it and informs the console.

## State and persistence
May delete the legacy local share file `urls.json`. Otherwise no runtime state.

## Dependencies and integration points
Integrates with the CLI command tree and share config helpers. Uses `os.Stat`, `os.Remove`, `filepath.Join`, `probe.NewError`, and console output.

## Risks and edge cases
- `migrateShare` removes legacy data rather than converting it into upload/download DBs.
- Migration does nothing if the share directory does not exist.

## Test signals
No direct tests. Tests could assert subcommand registration and migration deletion behavior.
