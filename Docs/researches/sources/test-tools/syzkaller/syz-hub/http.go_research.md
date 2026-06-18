## sources/test-tools/syzkaller/syz-hub/http.go

This file implements the syz-hub summary web page. `Hub.httpSummary` locks hub state, aggregates global corpus/repro counts and per-manager counters, sorts managers by name, prepends a total row, and renders an HTML template containing a manager table and cached log textarea.

The UI data types are `UISummaryData` and `UIManager`; `compileTemplate` injects static CSS into the HTML template. State is read under `hub.mu` from `state.State`, including manager HTTP URLs, domains, corpus sizes, add/delete/new counters, and repro counters.

Integration is with `hub.go` HTTP setup and syzkaller log cache. Risks include holding the hub lock while executing the template, minimal escaping relying on `html/template`, and total row not filling all fields in the same semantic way as managers. There are no direct tests for the HTML.
