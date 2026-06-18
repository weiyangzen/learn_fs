# sources/test-tools/syzkaller/pkg/html/pages/stats_test.go

## Purpose
`stats_test.go` verifies that the embedded stats page can render successfully.

## Important APIs, Types, And Functions
`TestStatsHTML` calls `StatsHTML` and reports any returned error through `t.Fatal`.

## Control Flow
The test invokes the render path once. Any package init parse panic or template execution error fails the test.

## State And Persistence Behavior
The test is in-memory and uses whatever graph data `stat.RenderGraphs` returns. It writes no files and performs no network calls.

## Dependencies And Integration Points
It depends only on Go `testing` directly, while indirectly covering `pages.Create`, embedded CSS/JS, `stats.html`, and `pkg/stat` graph rendering.

## Risks And Edge Cases
The test does not inspect rendered output, so missing sections, unsafe HTML, or broken client-side scripts can pass as long as template execution succeeds. It does not exercise `CreateFromFS`.

## Test Signals
This is a smoke test for stats template validity. It should fail quickly after incompatible changes to template fields or helper functions.
