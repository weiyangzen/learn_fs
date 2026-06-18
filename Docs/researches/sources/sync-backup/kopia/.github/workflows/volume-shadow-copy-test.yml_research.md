# sources/sync-backup/kopia/.github/workflows/volume-shadow-copy-test.yml

## Purpose
Validates Windows Volume Shadow Copy snapshot behavior on pushes, tags, and pull requests to `master`.

## APIs, Control Flow, and Integration Points
The workflow runs on `windows-latest`, checks out full source, installs Go, installs `gsudo` with Chocolatey, adds it to `GITHUB_PATH`, then runs `make os-snapshot-tests` twice: once elevated and once with `gsudo -i Medium` to simulate non-admin medium-integrity execution. Logs are uploaded on every result.

## State, Persistence, and Dependencies
State includes Windows-specific test artifacts, Go build outputs, and `.logs`. The Makefile target builds a testing binary and executes `tests/os_snapshot_test`. The workflow depends on Chocolatey, gsudo, Windows privilege behavior, and the host's VSS support.

## Risks and Test Signals
Privilege boundaries are the main risk: changes in hosted runner policy or gsudo behavior can affect the test independently of Kopia. Running both elevated and medium-integrity variants gives strong coverage for snapshot code that must behave under different user privileges.
