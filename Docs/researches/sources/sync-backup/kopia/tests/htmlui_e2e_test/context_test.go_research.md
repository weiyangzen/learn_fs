
# sources/sync-backup/kopia/tests/htmlui_e2e_test/context_test.go

## Purpose
Provides small `chromedp` helper context for HTML UI end-to-end tests: expected dialog handling state, logging actions, download completion wait, and screenshot capture.

## Important APIs, Types, And Functions
- `TestContext` stores `testing.T`, screenshot counter/path, expected dialog text/response, and a download completion channel.
- `expectDialogText` records the next expected JavaScript dialog text and response value.
- `log` wraps `t.Log` as a chromedp action.
- `waitForDownload` blocks on `downloadFinished` or times out.
- `captureScreenshot` writes numbered PNG screenshots under `screenshotsDir`.

## Control Flow
Each helper returns a `chromedp.ActionFunc` so UI tests can compose logging, dialog setup, download waiting, and screenshots inside `chromedp.Run`.

## State And Persistence Behavior
Persists screenshots to disk and tracks per-test screenshot numbering in memory. Dialog expectations are mutable test state read by the `chromedp.ListenTarget` callback in `htmlui_e2e_test.go`.

## Dependencies And Integration Points
Uses `chromedp`, `pkg/errors`, and the parent UI e2e runner. Screenshot paths are set by `runInBrowser`.

## Risks And Edge Cases
Dialog expectation state is mutable and not protected by a mutex, but tests run one browser flow per context. Download wait depends on browser events being enabled before clicking the downloadable link.

## Test Signals
Provides support signal for browser e2e diagnostics and failure artifacts.
