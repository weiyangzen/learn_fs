
# sources/sync-backup/kopia/tests/htmlui_e2e_test/htmlui_e2e_test.go

## Purpose
Runs opt-in browser end-to-end tests for Kopia HTML UI: repository creation, snapshot creation, snapshot browsing/download, connect/reconnect forms, theme switching, and byte-size representation preferences.

## Important APIs, Types, And Functions
- `runInBrowser` gates tests on `HTMLUI_E2E_TEST`, starts `kopia server start --ui`, configures `chromedp`, listens for JavaScript dialogs and download events, then runs a test callback.
- `createTestSnapshot` drives the UI to create a filesystem repository, estimate a new snapshot, create it, and return to the snapshot list.
- `TestEndToEndTest` browses snapshots and downloads an object.
- `TestConnectDisconnectReconnect` validates password mismatch dialog and repository setup path; disconnect portions are skipped due to timeout.
- `TestChangeTheme` cycles through `light`, `pastel`, `dark`, `ocean`, and back to `light`.
- `TestByteRepresentation` toggles base-2/base-10 byte preferences and checks displayed values.
- `TestPagination` is explicitly skipped.

## Control Flow
The test starts a local server with insecure/no-password settings for browser convenience, optionally points at `HTMLUI_BUILD_DIR`, configures screenshots under `../../.screenshots/htmlui-e2e-test/<test>`, launches Chrome headless in CI, navigates by `data-testid` selectors, and captures screenshots after key steps.

## State And Persistence Behavior
Creates filesystem repositories, source files including a 10 MB sparse/truncated file, UI preferences, screenshots, downloaded files, and browser state. The server process is killed and waited on by deferred callbacks.

## Dependencies And Integration Points
Uses `chromedp`, CDP browser/page events, `testenv`, `testutil.ServerParameters`, Kopia UI selectors, optional `HTMLUI_BUILD_DIR`, and env gates `HTMLUI_E2E_TEST`, `HTMLUI_TEST_PAUSE`, and `CI`.

## Risks And Edge Cases
Highly sensitive to UI selector changes, browser availability, timing, and CI headless behavior. The server flags combine `--insecure` and `--without-password`; this is test-only and should not be generalized. Disconnect flows are currently skipped inline due to timeout, reducing coverage.

## Test Signals
Opt-in high-level signal for critical UI workflows and visual/debug artifacts through screenshots.
