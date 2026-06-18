# sources/sync-backup/syncthing/.github/workflows/update-docs-translations.yaml

Purpose: scheduled/manual workflow for refreshing translations, documentation, contributor lists, and man pages.

Important APIs/types/functions: job checks out full history with write token, sets up stable Go, configures release automation Git identity, runs `bash build.sh translate`, then `bash build.sh prerelease`, and pushes the resulting commit. It consumes `WEBLATE_TOKEN`.

Control flow: `build.sh translate` delegates to `build.go translate`; `build.sh prerelease` runs authors/copyright scripts, Weblate update, manpage refresh, stages `gui`, `man`, and `AUTHORS`, and commits a fixed chore message.

State and persistence behavior: writes and pushes repository commits containing generated docs/translations/contributor metadata.

Dependencies/integration: depends on Go scripts under `script`, Weblate credentials, man refresh tooling, and clean commit generation.

Risks/test signals: scheduled commits can conflict with active changes or produce empty commits if no changes exist. Signal is a pushed chore commit with expected generated files, or a clear no-op/failure if nothing changed.
