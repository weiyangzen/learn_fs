# sources/sync-backup/kopia/.github/workflows/htmlui-tests.yml

## Purpose
Runs Kopia HTML UI end-to-end coverage on macOS for pull requests to `master`, pushes to `master` and `artifacts-pr`, and version tags. It specifically validates the Electron-backed UI path by invoking the repository's Makefile target.

## APIs, Control Flow, and Integration Points
The workflow sets shared Makefile environment flags, including `UNIX_SHELL_ON_WINDOWS`, `ENABLE_UNICODE_FILENAMES` from secrets, and `ENABLE_LONG_FILENAMES=false` because simulated keystrokes can be unreliable with long filenames. The single job checks out the full repository history, installs Go from `go.mod`, installs `gotestsum` via `make install-gotestsum`, then runs `make htmlui-e2e-test`. Screenshots under `.screenshots/**/*.png` are uploaded on every outcome.

## State, Persistence, and Dependencies
State is mostly transient: checked-out source, Go tooling, npm/Electron dependencies reached through Makefile targets, screenshots, and generated logs. The `concurrency` key cancels superseded UI runs for the same workflow/ref pair.

## Risks and Test Signals
The workflow only runs on `macos-latest`, so Linux-specific AppArmor and Windows UI packaging behaviors are outside this lane. It relies on Makefile and app package scripts to provision Node dependencies. The test signal is focused and user-facing: `HTMLUI_E2E_TEST=1` exercises `tests/htmlui_e2e_test`, while screenshot artifacts support debugging visual or interaction failures.
