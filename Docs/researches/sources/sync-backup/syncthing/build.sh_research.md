# sources/sync-backup/syncthing/build.sh

Purpose: shell wrapper around `build.go` and selected scripts. It provides short commands for test, benchmark, prerelease maintenance, and default build delegation.

Important APIs/types/functions: helper `script()` runs `go run script/<name>.go`; helper `build()` runs `go run build.go`. Cases are `test`, `bench`, `prerelease`, and default passthrough.

Control flow: strict Bash mode is enabled. `test` and `bench` set `LOGGER_DISCARD=1` before invoking build commands. `prerelease` regenerates authors, copyrights, Weblate translations, man pages, stages generated docs/translations/contributors, and commits a fixed chore message.

State and persistence behavior: default/test/bench mostly produce build/test artifacts. `prerelease` mutates `gui`, `man`, and `AUTHORS`, and creates a Git commit.

Dependencies/integration: used by the docs/translations workflow and by developers. It depends on Go scripts, `build.go`, manpage refresh script, Git, and Weblate credentials for translation updates.

Risks/test signals: `prerelease` assumes a clean worktree and may fail on no changes or conflicts. The signal is successful wrapper execution and, for prerelease, a generated commit containing only intended maintenance outputs.
