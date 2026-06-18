# sources/object-store/minio-mc/cmd/speedtest-spinner.go

## Purpose
Implements Bubble Tea UI rendering for MinIO speed test progress and final summaries across object, network, site replication, drive, and client performance tests.

## Important APIs, types, and functions
- `speedTestUI` is the Bubble Tea model with spinner, quit state, and current `PerfTestResult`.
- `PerfTestType` identifies test categories and `Name` maps values to display names.
- `PerfTestResult` carries one of several `madmin` speed test result types, an error, and a final flag.
- `initSpeedTestUI`, `Init`, `Update`, and `View` implement Bubble Tea lifecycle.

## Control flow
`Update` handles key presses (`q`, `esc`, `ctrl+c`) by quitting, handles `PerfTestResult` messages by storing the latest result and quitting when final, and delegates other messages to the spinner. `View` returns an error view if `Err` is set, otherwise builds a table for whichever result pointer/slice is populated. During non-final state it shows an animated spinner; final state shows a tick and, for object tests, appends short and optional verbose results.

## State and persistence
In-memory UI state only. No persistence. It reads global `globalPerfTestVerbose` to decide extra object-test output.

## Dependencies and integration points
Uses Bubble Tea (`tea`), Bubbles spinner, Lip Gloss styles, `madmin-go` performance result structs, `tablewriter`, `humanize`, global symbols such as `tickCell`, `crossTickCell`, `objectTestShortResult`, and `objectTestVerboseResult`.

## Risks and edge cases
- `View` chooses the first non-nil result in a fixed order; malformed messages with multiple populated result fields will hide later fields.
- Site replication rate divides by whole seconds and explicitly handles zero duration.
- Endpoint strings are truncated to 64 characters.
- Drive result ordering is whatever server result order provides; network and site rows are sorted.

## Test signals
No direct tests. UI tests could feed `PerfTestResult` messages and assert rendered output for empty, error, final, and zero-duration cases.
