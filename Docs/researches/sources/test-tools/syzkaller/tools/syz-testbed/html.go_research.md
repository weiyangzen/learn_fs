# sources/test-tools/syzkaller/tools/syz-testbed/html.go

## Purpose
This file implements the live HTTP dashboard for `syz-testbed`, rendering summary/stat tables and graph images from current testbed state.

## Important APIs, types, and functions
- `setupHTTPServer` installs handlers for `/`, `/graph`, and `/favicon.ico` and serves with gzip compression.
- `getCurrentStatView` selects requested, first non-empty, or first available stat view.
- `httpGraph` materializes averaged bench files, invokes external `syz-benchcmp`, and writes generated graph output.
- UI structs `uiTable`, `uiTableType`, `uiStatView`, and `uiMainPage` carry data to templates.
- `getTableTypes`, `genSimpleTableController`, `httpMainStatsTable`, `httpMain`, and `executeTemplate` generate table views.
- Embedded templates are loaded from `templates/*.html` through `pages.CreateFromFS`.

## Control flow
The main page selects an active view and table type from query parameters, builds URL callbacks for table/view navigation, generates the active table, and executes `testbed.html`. Stats table links can set `base_column` and `align` parameters, causing `Table.SetRelativeValues` and aligned stats generation. Graph requests create temp dirs/files, save average benches, run `benchcmp -all -over ... -out ...`, and stream the output.

## State and persistence behavior
The server reads live in-memory checkout state via `GetStatViews`. Graph requests create temporary files/directories and remove them with defers. No persistent dashboard state is stored by this file.

## Dependencies and integration points
Uses Go `net/http`, embedded templates, `gorilla/handlers` compression, `pkg/html/pages`, `pkg/osutil`, and local stats/table generation. Depends on `ctx.Target.SupportsHTMLView` to present target-appropriate tables.

## Risks and edge cases
`setupHTTPServer` is always called even if `ctx.Config.HTTP` is empty; listen behavior depends on config validation/defaults. In `httpMain`, an unknown table key writes `fmt.Sprintf("%s", err)` where `err` may be nil, producing a confusing response. `httpGraph` shells out to an external benchcmp path for every request and can be expensive. Template map iteration can make table-type link order nondeterministic.

## Test signals
No direct tests. Useful tests include view/table query selection, invalid view/table handling, relative-value links, graph failure paths, and template execution over empty/non-empty stats.
