# sources/test-tools/syzkaller/pkg/html/pages/stats.go

## Purpose
`stats.go` renders syzkaller statistics graphs as embeddable HTML.

## Important APIs, Types, And Functions
`StatsHTML() (template.HTML, error)` renders the embedded `stats.html` template using graph data from `stat.RenderGraphs`. `statsTemplate` is initialized with `Create(statsHTML)`. `statsHTML` is embedded at compile time.

## Control Flow
`StatsHTML` creates a buffer, obtains render data from `stat.RenderGraphs`, executes the pre-parsed template into the buffer, wraps execution errors with context, and returns the rendered string as `template.HTML`.

## State And Persistence Behavior
The template is parsed at package initialization and retained globally. Rendering is in-memory. Returning `template.HTML` marks the output as trusted to callers, so escaping responsibility lies in template construction and data safety.

## Dependencies And Integration Points
The file imports `pkg/stat` for graph data, `html/template` for the trusted HTML type, and uses `pages.Create` to include common CSS/JS and template functions. It is likely consumed by dashboard pages that embed stats blocks.

## Risks And Edge Cases
Package initialization panics if the embedded template cannot parse. Because output is marked trusted, any unescaped unsafe data in `stats.html` or `stat.RenderGraphs` would bypass downstream escaping. Errors are only possible during execution, not parse, because parse already happened globally.

## Test Signals
`stats_test.go` calls `StatsHTML` and fails on execution error, catching template/data mismatches and parse-time issues during test startup.
